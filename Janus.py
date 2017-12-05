import numpy as np
import pFDMAC

packet_length_list = [64,128,256,512,1024,1500]

#the packet length setting
p_CFPoll_header = 18
p_FCS = 4
p_Interfere_info = 4 # (nodeid + interfere level)*2
p_ACK = p_CFPoll_header + p_Interfere_info
ACK = 14
p_Data = 2048

# Frame space setting (us)
T_SLOT = 8#20
T_SIFS = 10
T_PIFS = T_SIFS + T_SLOT
T_DIFS = T_SIFS + 2*T_SLOT
T_EIFS = T_SIFS + T_DIFS +T_SLOT

Vt = 18 #Mbps
########################################################################################################################

########################################################################################################################
# compare with Janus
########################################################################################################################
def getUnvisited(visited, num_stations):
    tmp = []
    for i in range(num_stations):
        tmp.append(i)
    for i in visited:
        tmp.remove(i)
    return  tmp

def calcLF(outputlength, rate_new, rate_old):
    return outputlength/rate_new - outputlength/rate_old

def calcDeltaCompletion(inputlength, outputlength, OutID, inID):
    T_fullduplex = ()

def add2schedulingTime(upstream, downstream):
    schedueNum  = np.sum((np.array(upstream)>0).astype(np.int8))
    schedueNum += np.sum((np.array(downstream)>0).astype(np.int8))

    return schedueNum*45

def Janus_sim_overhead(upstream, downstream):
    # calculate the overhead: preparation time and ACK time
    Janus_timer = 0
    Janus_timer += 800 # request flag, ACK and so on
    Janus_timer += len(upstream) * 44 # uploading packet request
    #scheduer time: 45us per packet
    Janus_timer += add2schedulingTime(upstream, downstream)
    return Janus_timer

def Janus_sim_exchange_period(upstream, downstream, matSIR, curr_down_time=0, curr_up_time=0, last_dSta = -1, last_uSta = -1, last_op_rate = 0, last_packet_length = 0):
    uVistedStation = []
    dVistedStation = []
    stationNum = len(upstream)

    for i in range(len(upstream)):
        if upstream[i] == 0:
            uVistedStation.append(i)
        if downstream[i] == 0:
            dVistedStation.append(i)

    while(True):
        uUnVisited = getUnvisited(uVistedStation, stationNum)
        dUnVisited = getUnvisited(dVistedStation, stationNum)
        if not uUnVisited:
            if not dUnVisited:
                return curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length
            else:
                if curr_down_time >= curr_up_time:
                    for i in dUnVisited:
                        curr_down_time += T_SIFS + (p_CFPoll_header + downstream[i] + p_FCS)/Vt*8
                    last_dSta = dUnVisited[-1]
                    last_op_rate = Vt
                    last_packet_length = downstream[last_dSta]
                    return curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length
        if not dUnVisited:
            if not uUnVisited:
                return curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length
            else:
                if curr_up_time >= curr_down_time:
                    for i in uUnVisited:
                        curr_up_time += T_SIFS + (p_CFPoll_header + upstream[i] + p_FCS)/Vt*8
                    last_uSta = uUnVisited[-1]
                    return curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length

        if curr_down_time == curr_up_time:
            tmp_uSta = uUnVisited[0]
            curr_up_time += T_SIFS + (p_CFPoll_header + upstream[tmp_uSta] + p_FCS)/Vt*8
            uVistedStation.append(tmp_uSta)
            last_uSta = tmp_uSta
        elif curr_up_time > curr_down_time:
            if last_uSta == -1:
                print('last upload station is wrong!')
                break

            LF_V = []
            DeltaT = []

            for dSta in dUnVisited:
                op_rate = pFDMAC.lookupRate(matSIR[last_uSta][dSta])

                if op_rate == 0:
                    LF_V.append(0)
                    DeltaT.append(0)
                elif op_rate > 0:
                    LF_V.append(calcLF(downstream[dSta], op_rate, Vt))
                    down_time_alone = curr_up_time + T_SIFS + (p_CFPoll_header + downstream[dSta] + p_FCS)/Vt*8
                    down_time_concurrent = curr_down_time + T_SIFS + (p_CFPoll_header + downstream[dSta] + p_FCS)/op_rate*8
                    DeltaT.append(down_time_alone - down_time_concurrent)
                else:
                    print("haha mistake!!!")

            if max(DeltaT) <= 0:
                curr_down_time = curr_up_time
                continue
            else:
                d_index = 0
                flag = True
                for i in range(len(DeltaT)):
                    if DeltaT[i] > 0:
                        if flag:
                            tmp_v = LF_V[i]
                            d_index = i
                            flag = False
                        elif tmp_v > LF_V[i]:
                            tmp_v = LF_V[i]
                            d_index = i

                last_dSta = dUnVisited[d_index]
                last_op_rate = pFDMAC.lookupRate(matSIR[last_uSta][last_dSta])
                if last_op_rate == 0:
                    print("kidding me??")
                last_packet_length = downstream[last_dSta]

                curr_down_time += T_SIFS + (p_CFPoll_header + downstream[last_dSta] + p_FCS)/last_op_rate*8
                dVistedStation.append(last_dSta)
        elif curr_down_time > curr_up_time:
            if last_dSta == -1:
                print('last down station is wrong!')
                break

            LF_V = []
            DeltaT = []

            for uSta in uUnVisited:
                op_rate = pFDMAC.lookupRate(matSIR[uSta][last_dSta])
                if op_rate == 0:
                    LF_V.append(0)
                    DeltaT.append(0)
                    continue
                # if it can introduce a less amount of interference on an unscheduled outgoning queue, ignore it
                flag = False
                for dSta in dUnVisited:
                    op_rate1 = pFDMAC.lookupRate(matSIR[uSta][dSta])
                    if op_rate1 > op_rate:
                        flag = True
                        break
                if flag:
                    # print('the upload stations may be has a better choice!')
                    LF_V.append(0)
                    DeltaT.append(0)
                    continue

                if op_rate >= last_op_rate:
                    deltaDowntime = 0
                else:
                    deltaDowntime = calcLF(last_packet_length, op_rate, last_op_rate)
                LF_V.append(deltaDowntime)
                up_time_alone = curr_down_time + T_SIFS + (p_CFPoll_header + upstream[uSta] + p_FCS)/Vt*8
                up_time_concurrent = curr_up_time + T_SIFS + (p_CFPoll_header + upstream[uSta] + p_FCS)/Vt*8
                DeltaT.append(up_time_alone - max(up_time_concurrent, curr_down_time + deltaDowntime))

            if max(DeltaT) <= 0:
                curr_up_time = curr_down_time
            else:
                u_index = 0
                flag = True
                for i in range(len(DeltaT)):
                    if DeltaT[i] > 0:
                        if flag:
                            tmp_v = LF_V[i]
                            u_index = i
                            flag = False
                        if tmp_v >= LF_V[i]:
                            tmp_v = LF_V[i]
                            u_index = i
                last_uSta = uUnVisited[u_index]
                op_rate = pFDMAC.lookupRate(matSIR[last_uSta][last_dSta])
                if op_rate <= 0:
                    print("how this happend??")
                if op_rate >= last_op_rate:
                    deltaDowntime = 0
                else:
                    deltaDowntime = calcLF(last_packet_length, op_rate, last_op_rate)
                    last_op_rate = op_rate
                curr_up_time += T_SIFS + (p_CFPoll_header + upstream[last_uSta] + p_FCS)/Vt*8
                if deltaDowntime > 0:
                    curr_down_time += deltaDowntime
        else:
            print('Something is wrong!')
    return curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length

def Janus_sim_exchange_period_old(upstream, downstrem, curr_time, matSIR):
    # start exchange peirod
    curr_up_time = curr_time
    curr_down_time = curr_time
    up_visted = []
    down_visited = []
    down_visited_rate = []

    last_uSta = -1
    last_dSta = -1
    for i in range(len(upstream)):
        if upstream[i] == 0:
            up_visted.append(i)
        if downstrem[i] == 0:
            down_visited.append(i)

    while(True):
        upUnvisited = getUnvisited(up_visted, len(upstream))
        downUnvisited = getUnvisited(down_visited, len(downstrem))
        if not upUnvisited:
            if not downUnvisited:
                return max(curr_down_time,curr_up_time)
            else:
                if curr_down_time >= curr_up_time:
                    for i in downUnvisited:
                        curr_down_time += T_SIFS + (p_CFPoll_header + downstrem[i] + p_FCS)/Vt*8
                    return max(curr_down_time, curr_up_time)
        if not downUnvisited:
            if not upUnvisited:
                return max(curr_down_time, curr_up_time)
            else:
                if curr_up_time >= curr_down_time:
                    for i in upUnvisited:
                        curr_up_time += T_SIFS + (p_CFPoll_header + upstream[i] + p_FCS)/Vt*8
                    return max(curr_down_time, curr_up_time)

        if curr_down_time == curr_up_time:
            station_ID = upUnvisited[0]
            up_visted.append(station_ID)
            curr_up_time += T_SIFS + (p_CFPoll_header + upstream[station_ID] + p_FCS) / Vt*8
            last_uSta = station_ID
        elif curr_up_time > curr_down_time:
            downUnvisited = getUnvisited(down_visited, len(downstrem))
            LF_v = []
            deltaT = []
            for i in downUnvisited:
                tmp_rate = pFDMAC.lookupRate(matSIR[last_uSta][i])
                if tmp_rate > 0:
                    LF_v.append(calcLF(downstrem[i],tmp_rate,Vt))
                    deltaT.append(curr_up_time - curr_down_time - calcLF(downstrem[i],tmp_rate,Vt))
                else:
                    deltaT.append(0)
                    LF_v.append(0)

            if max(deltaT) <= 0:
                curr_down_time = curr_up_time
                continue
            else:
                ind = downUnvisited[LF_v.index(min(LF_v))]

                curr_down_time += (p_CFPoll_header + downstrem[ind] + p_FCS)/pFDMAC.lookupRate(matSIR[ind][station_ID])*8
                down_visited.append(ind)
                down_visited_rate.append(pFDMAC.lookupRate(matSIR[ind][station_ID]))
        else:
            T_full = curr_down_time - curr_up_time
            LF_v = []
            deltaT = []
            optionlist = []
            LF_value = []
            for i in upUnvisited:
                # calculate delta time of completion
                last_station = down_visited[-1]
                op_rate = pFDMAC.lookupRate(matSIR[last_station][i])

                if op_rate == 0:
                    continue

                if op_rate >= down_visited_rate[-1]:
                    deltaT.append(T_full)
                    LF_v.append(calcLF(downstrem[last_station],op_rate,down_visited_rate[-1]))
                    optionlist.append(i)
                    LF_value.append(calcLF(downstrem[last_station],op_rate,down_visited_rate[-1]))
                    continue

                T1 = (p_CFPoll_header + upstream[i] + p_FCS)/Vt*8
                T_tmp = T_full + calcLF(p_CFPoll_header + downstrem[last_station] + p_FCS,op_rate,down_visited_rate[-1])

                if T1 + T_SIFS >= T_tmp:
                    deltaT.append(T_full)
                    LF_v.append(calcLF(downstrem[last_station], op_rate, down_visited_rate[-1]))
                    optionlist.append(i)
                    LF_value.append(calcLF(downstrem[last_station], op_rate, down_visited_rate[-1]))
                else:
                    deltaT.append(T_full + T1 + T_SIFS - T_tmp)
                    LF_v.append(calcLF(downstrem[last_station], op_rate, down_visited_rate[-1]))
                    if T_full + T1 + T_SIFS - T_tmp > 0:
                        optionlist.append(i)
                        LF_value.append(calcLF(downstrem[last_station], op_rate, down_visited_rate[-1]))

            if not optionlist:
                curr_up_time = curr_down_time
            else:
                for i in optionlist:
                    downUnvisited = getUnvisited(down_visited,len(downstrem))
                    flag = False
                    for j in downUnvisited:
                        if pFDMAC.lookupRate(matSIR[j][i]) > pFDMAC.lookupRate(matSIR[down_visited[-1]][i]):
                            flag = True
                            break
                    if flag:
                        LF_value.remove(LF_value[optionlist.index(i)])
                        optionlist.remove(i)

                if not optionlist:
                    curr_up_time = curr_down_time
                else:
                    upindex = optionlist[LF_value.index(min(LF_value))]

                    curr_up_time += T_SIFS + (p_CFPoll_header + upstream[upindex] + p_FCS)/Vt*8
                    up_visted.append(upindex)

    curr_time = max(curr_down_time, curr_up_time)
    return curr_time

def Janus_sim_old(upstream,downstream, matSIR, flag = True):
    overheadtime = Janus_sim_overhead(matSIR)
    if flag:
        current_time = Janus_sim_exchange_period_old(upstream, downstream, overheadtime, matSIR)
        current_time = Janus_sim_exchange_period_old(upstream, downstream, current_time, matSIR)
    else:
        current_time = Janus_sim_exchange_period_old(upstream, downstream, overheadtime, matSIR)

    return current_time
