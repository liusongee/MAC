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

Vt = 18/8 #Mbps
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

def Janus_sim_overhead(matSIR):
    # calculate the overhead: preparation time and ACK time
    Janus_timer = 0
    Janus_timer += (p_CFPoll_header + p_FCS)/Vt + T_DIFS
    Janus_timer += (p_CFPoll_header + len(matSIR) + p_FCS)/Vt + T_SIFS
    for i in range(len(matSIR)):
        probe_packet = p_CFPoll_header + 2 + p_FCS
        for j in range(len(matSIR)):
            if i == j:
                continue
            if matSIR[i][j] < 20:
                probe_packet += 2

        Janus_timer += probe_packet/Vt + T_SIFS

    Janus_timer += 2500 # scheduling time
    return Janus_timer

def Janus_sim_exchange_period(upstream, downstrem, curr_time, matSIR):
    # start exchange peirod
    curr_up_time = curr_time
    curr_down_time = curr_time
    up_visted = []
    down_visited = []
    down_visited_rate = []
    down_visited_Dtime = []

    V_curr = Vt
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
                        curr_down_time += T_SIFS + (p_CFPoll_header + downstrem[i] + p_FCS)/Vt
                    return max(curr_down_time, curr_up_time)
        if not downUnvisited:
            if not upUnvisited:
                return max(curr_down_time, curr_up_time)
            else:
                if curr_up_time >= curr_down_time:
                    for i in upUnvisited:
                        curr_up_time += T_SIFS + (p_CFPoll_header + upstream[i] + p_FCS)/Vt
                    return max(curr_down_time, curr_up_time)

        if curr_down_time == curr_up_time:
            station_ID = upUnvisited[0]
            up_visted.append(station_ID)
            curr_up_time += T_SIFS + (p_CFPoll_header + upstream[station_ID] + p_FCS) / Vt
        elif curr_up_time > curr_down_time:
            downUnvisited = getUnvisited(down_visited, len(downstrem))
            LF_v = []
            deltaT = []
            for i in downUnvisited:
                tmp_rate = pFDMAC.lookupRate(matSIR[i][station_ID])
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

                curr_down_time += (p_CFPoll_header + downstrem[ind] + p_FCS)/pFDMAC.lookupRate(matSIR[ind][station_ID])
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

                T1 = (p_CFPoll_header + upstream[i] + p_FCS)/Vt
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

                    curr_up_time += T_SIFS + (p_CFPoll_header + upstream[upindex] + p_FCS)/Vt
                    up_visted.append(upindex)

    curr_time = max(curr_down_time, curr_up_time)
    return curr_time

def Janus_sim(upstream,downstream, matSIR, flag = True):
    overheadtime = Janus_sim_overhead(matSIR)
    if flag:
        current_time = Janus_sim_exchange_period(upstream, downstream, overheadtime, matSIR)
        current_time = Janus_sim_exchange_period(upstream, downstream, current_time, matSIR)
    else:
        current_time = Janus_sim_exchange_period(upstream, downstream, overheadtime, matSIR)

    return current_time
