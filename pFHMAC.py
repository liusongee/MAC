# this is a simulator for pFHMAC, polling based full-/half-duplex MAC protocol
import numpy as np
from globalPara import *
import trafficHandler as trafficH
import random
################################################################################
# global parameter settting
################################################################################
def lookupRate(SIR):
    for i in range(len(op_rate_list_SIR)):
        if SIR > op_rate_list_SIR[i][0]:
            return op_rate_list_SIR[i][1]
    return 0

def getUnvisitedStations(visitedStations, num_stations):
    tmp = []
    for i in range(num_stations):
        tmp.append(i)
    for i in visitedStations:
        tmp.remove(i)
    return tmp

def contention_free_inital_stage_sim(mat_SIR):
    num_stations = len(mat_SIR)
    packet_length_info = 1
    L_probe_packet = p_CFPoll_header + packet_length_info + p_FCS

    curr_down_time = 0
    curr_up_time = 0
    for i in range(num_stations):
        # send a probe packet
        curr_down_time = curr_up_time + T_SIFS + L_probe_packet*8/V_max
        # receive a reply packet from a station
        L_probe_reply_packet = p_CFPoll_header + packet_length_info + p_FCS
        for j in range(num_stations):
            if i == j:
                continue
            if mat_SIR[i][j] < 20:
                L_probe_reply_packet += 2

        curr_up_time = curr_down_time + T_SIFS + L_probe_reply_packet*8/V_max

    return [max(curr_down_time, curr_up_time), max(curr_down_time, curr_up_time)]
#
def greedyPolling(matSIR, upstream, downstream, curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, op_rate_last= 0, last_Dpayload = 0):
    ackflag_up = np.array(upstream) > 0
    ackflag_down = np.array(downstream) > 0
    ackflag_up = ackflag_up.astype(np.int32)
    ackflag_down = ackflag_down.astype(np.int32)

    tmp1 = np.array(upstream) + ACK_down * 14
    tmp2 = np.array(downstream) + ACK_up * 14

    upstream = tmp1.tolist()
    downstream = tmp2.tolist()

    uVisitedStations = []
    dVisitedStations = []

    uUnvisitedStation = getUnvisitedStations(uVisitedStations, len(upstream))
    dUnvisitedStation = getUnvisitedStations(dVisitedStations, len(downstream))

    while(uUnvisitedStation or dUnvisitedStation):
        delta_time = []
        concurrent_time = []
        alone_time = []
        if curr_up_time == curr_down_time:
            # random select a downstream packet
            dStation = random.choice(dUnvisitedStation)
            # look for a station can concurrently send packets
            for upS in uUnvisitedStation:
                op_rate = lookupRate(matSIR[upS][dStation])
                if op_rate <= 0:
                    delta_time.append(0)
                    concurrent_time.append([0,0])
                    alone_time.append([0,0])
                else:
                    curr_down_time_concurrent = curr_down_time + T_SIFS + (p_CFPoll_header + downstream[dStation] + p_FCS)*8/op_rate
                    curr_up_time_concurrent = curr_down_time + T_SIFS + (2*p_CFPoll_header + upstream[upS] + p_FCS)*8/V_max

                    curr_down_time_alone = curr_down_time + T_SIFS + (p_CFPoll_header + downstream[dStation] + p_FCS)*8/V_max
                    curr_up_time_alone = curr_down_time_alone + T_SIFS + (p_CFPoll_header + upstream[upS] + p_FCS)*8/V_max

                    delta_time.append(max(curr_down_time_concurrent, curr_up_time_concurrent) - curr_up_time_alone)
                    concurrent_time.append([curr_down_time_concurrent,curr_up_time_concurrent])
                    alone_time.append([curr_down_time_alone,curr_up_time_alone])

            if min(delta_time) >= 0:
                # random select a upstream packet
                if dStation in uUnvisitedStation:
                    uStation = dStation
                else:
                    uStation = random.choice(uUnvisitedStation)
                # send packet in serial
                curr_down_time = curr_down_time + T_SIFS + (p_CFPoll_header + downstream[dStation] + p_FCS)*8/V_max
                curr_up_time = curr_down_time + T_SIFS + (p_CFPoll_header + upstream[uStation] + p_FCS)*8/V_max

                last_station = [dStation, uStation]
                dVisitedStations.append(dStation)
                uVisitedStations.append(uStation)
                # adjust curr_down_time
                curr_down_time = curr_up_time - T_SIFS - (upstream[uStation] + p_FCS) * 8 / V_max
            else:
                min_uStation_i = delta_time.index(min(delta_time))
                if dStation in uUnvisitedStation and delta_time[min_uStation_i] == delta_time[uUnvisitedStation.index(dStation)]:
                    min_uStation_i = uUnvisitedStation.index(dStation)
                curr_down_time = concurrent_time[min_uStation_i][0]
                curr_up_time = concurrent_time[min_uStation_i][1]
                last_station = [dStation, uUnvisitedStation[min_uStation_i]]
                dVisitedStations.append(dStation)
                uVisitedStations.append(uUnvisitedStation[min_uStation_i])
                # avoid polling one more station
                if curr_up_time < curr_down_time:
                    curr_up_time = curr_down_time
        elif curr_up_time > curr_down_time:
            op_rate_list = []
            # schedule downstream packet
            for downS in dUnvisitedStation:
                # calculate the concurrent time
                op_rate = lookupRate(matSIR[last_station[1]][downS])

                if op_rate <= 0:
                    delta_time.append(0)
                    concurrent_time.append([0,0])
                    alone_time.append([0,0])
                    op_rate_list.append(0)
                else:
                    curr_down_time_concurrent = curr_down_time + T_SIFS + (p_CFPoll_header +downstream[downS] + p_FCS)*8 / op_rate
                    curr_up_time_concurrent = curr_up_time

                    # calculate the time of send packets alone
                    curr_down_time_alone = curr_up_time + T_SIFS + (p_CFPoll_header + downstream[
                        downS] + p_FCS) * 8 / V_max
                    curr_up_time_alone = curr_up_time
                    delta_time.append(curr_down_time_concurrent - curr_down_time_alone)
                    concurrent_time.append([curr_down_time_concurrent, curr_up_time_concurrent])
                    alone_time.append([curr_down_time_alone, curr_up_time_alone])
                    op_rate_list.append(op_rate)

            if min(delta_time) >= 0:
                curr_down_time = curr_up_time
                op_rate_last = 0
                last_Dpayload = 0
                continue
            else:
                min_dStation_i = delta_time.index(min(delta_time))

                curr_down_time = concurrent_time[min_dStation_i][0]
                last_station[0] = dUnvisitedStation[min_dStation_i]
                dVisitedStations.append(last_station[0])
                op_rate_last = op_rate_list[min_dStation_i]
                last_Dpayload = downstream[last_station[0]]

            if curr_down_time <= curr_up_time:
                # upload a packet
                if last_station[0] in uUnvisitedStation:
                    uStation = last_station[0]
                else:
                    uStation = random.choice(uUnvisitedStation)
                curr_down_time = curr_up_time + p_CFPoll_header * 8 / V_max
                curr_up_time = curr_up_time + T_SIFS + (p_CFPoll_header + upstream[uStation] + p_FCS) * 8 / V_max
                last_station[1] = uStation
                uVisitedStations.append(uStation)
            elif curr_down_time > curr_up_time:
                # schedule upstream packet
                delta_time = []
                concurrent_time = []
                alone_time = []
                for upS in uUnvisitedStation:
                    # calculate send them parallelly
                    op_rate = lookupRate(matSIR[upS][last_station[0]])
                    if op_rate <= 0:
                        delta_time.append(0)
                        concurrent_time.append([0,0])
                        alone_time.append([0,0])
                        continue
                    elif op_rate_last <= op_rate:
                        if op_rate_last == 0:
                            print("operate transmission rate goes wrong!")
                            break
                        else:
                            curr_up_time_concurrent = max(curr_down_time - (last_Dpayload + p_FCS)*8/op_rate_last - T_SIFS, curr_up_time) + T_SIFS + (p_CFPoll_header + upstream[upS] + p_FCS) * 8 / V_max
                        curr_down_time_concurrent = curr_down_time
                    else:
                        curr_up_time_header = curr_down_time - (last_Dpayload + p_FCS)*8/op_rate_last - p_CFPoll_header*8*(1/op_rate_last - 1/op_rate)
                        curr_up_time_concurrent = max(curr_up_time_header, curr_up_time + T_SIFS) + (p_CFPoll_header + upstream[upS] + p_FCS) * 8 / V_max
                        curr_down_time_concurrent = curr_down_time + ((p_CFPoll_header + last_Dpayload + p_FCS) * 8)*(1/op_rate - 1/op_rate_last)
                    # calculate send them alone
                    curr_up_time_alone = curr_down_time + T_SIFS + (p_CFPoll_header + upstream[upS] + p_FCS) * 8 / V_max
                    curr_down_time_alone = curr_down_time

                    delta_time.append(max(curr_up_time_concurrent, curr_down_time_concurrent) - max(curr_up_time_alone, curr_down_time_alone))
                    concurrent_time.append([curr_down_time_concurrent, curr_up_time_concurrent])
                    alone_time.append([curr_down_time_alone, curr_up_time_alone])

                if min(delta_time) >= 0:
                    if last_station[0] in uUnvisitedStation:
                        uStation = last_station[0]
                    else:
                        uStation = random.choice(uUnvisitedStation)
                    curr_up_time = curr_down_time + T_SIFS + (p_CFPoll_header + upstream[uStation] + p_FCS) * 8 / V_max
                    curr_down_time += p_CFPoll_header*8/V_max

                    last_station[1] = uStation
                    uVisitedStations.append(uStation)
                else:
                    min_uStation_i = delta_time.index(min(delta_time))
                    if last_station[0] in uUnvisitedStation and delta_time[min_uStation_i] == delta_time[uUnvisitedStation.index(last_station[0])]:
                        min_uStation_i = uUnvisitedStation.index(last_station[0])
                    curr_up_time = concurrent_time[min_uStation_i][1]
                    curr_down_time = concurrent_time[min_uStation_i][0]
                    last_station[1] = uUnvisitedStation[min_uStation_i]
                    uVisitedStations.append(last_station[1])

                if curr_up_time < curr_down_time:
                    curr_up_time = curr_down_time
        else:
            # something is wrong.
            print("something is wrong!!")

        uUnvisitedStation = getUnvisitedStations(uVisitedStations, len(upstream))
        dUnvisitedStation = getUnvisitedStations(dVisitedStations, len(downstream))

    return curr_up_time, curr_down_time, last_station, ackflag_up, ackflag_down, op_rate_last, last_Dpayload
