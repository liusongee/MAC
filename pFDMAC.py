################################################################################
# simulate the pFDMAC protocol
################################################################################
import math
import numpy as np
import random

########################################################################################################################
## global parameter
########################################################################################################################
# Unit

# PHY layer
# MAC layer
# the packet length setting
p_CFPoll_header = 16
p_FCS = 4
p_Interfere_info = 4  # (nodeid + interfere level)*2
p_ACK = p_CFPoll_header + p_Interfere_info
ACK = 14
p_Payload = 1024

# Frame space setting (us)
T_SLOT = 8  # 20
T_SIFS = 10
T_PIFS = T_SIFS + T_SLOT
T_DIFS = T_SIFS + 2 * T_SLOT
T_EIFS = T_SIFS + T_DIFS + T_SLOT

Vt = 12 / 8  # Mbps
# select proper transmission rate according to the value of SIR
# V1_SIR = 17 # V1 = 12Mbps
# V2_SIR = 13 # V2 = 8Mbps
# V3_SIR = 12 # V3 = 6Mbps
op_rate_list_SIR = [[20, 18],
                    [18, 16],
                    [16, 12],
                    [13, 8],
                    [12, 6],
                    [10, 3]]
V_max = 18
################################################################################
def lookupRate(SIR):
    for i in range(len(op_rate_list_SIR)):
        if SIR > op_rate_list_SIR[i][0]:
            return op_rate_list_SIR[i][1]
    return 0

def listOfunvisited(visitedPath):
    tmp = []
    for i in range(visitedPath):
        tmp.append(i)

    for i in range(visitedPath):
        if visitedPath[i] != -1:
            tmp.remove(visitedPath[i])
    return tmp

def getUnvisitedStations(visitedStations, num_stations):
    tmp = []
    for i in range(num_stations):
        tmp.append(i)
    for i in visitedStations:
        tmp.remove(i)
    return tmp

# ACK_up: ACK of packet of upstream;
# ACK_down: ACK of packet of downstream
def greedyPolling_upWithVaryRate(matSIR, upstream, downstream, curr_up_time, curr_down_time, last_station, ACK_up=False, ACK_down=False, current_rate = V_max):
    V_curr = current_rate
    count = 0
    visitedStations = []
    while(count < len(upstream)):
        unvisitedStation = getUnvisitedStations(visitedStations,len(upstream))
        if not unvisitedStation:
            return [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr]
        delta_time = []
        concurrent_time = []
        alone_time = []
        if last_station != -1:
            for i in unvisitedStation:
                op_rate = lookupRate(matSIR[last_station][i])
                if op_rate >= V_curr:
                    # concurrent: using V_curr as the transmission rate
                    if curr_up_time <= curr_down_time:
                        delta_time.append(0)
                        concurrent_time.append([0,0])
                        alone_time.append([0,0])
                        continue

                    if ACK_down:
                        curr_up_time_concurrent = curr_up_time + T_SIFS + ACK*8/V_curr
                    else:
                        curr_up_time_concurrent = max(curr_up_time, curr_down_time)

                    curr_down_time_concurrent = curr_down_time + T_SIFS + (p_CFPoll_header + downstream[i] + p_FCS)*8/V_curr

                    if ACK_up:
                        curr_down_time_concurrent = max(curr_down_time_concurrent, curr_up_time_concurrent) + T_SIFS + ACK*8/V_curr
                        ACK_up_transfered = True
                    curr_up_time_concurrent += T_SIFS + (p_CFPoll_header + 1 + upstream[i] + p_FCS)*8/V_curr
                    curr_time_concurrent = max(curr_up_time_concurrent, curr_down_time_concurrent)

                    # alone: using maximal transmission rate as current transmission rate
                    curr_down_time_alone = max(curr_up_time, curr_down_time)
                    curr_up_time_alone = max(curr_up_time, curr_down_time)
                    if ACK_up:
                        curr_down_time_alone = max(curr_up_time, curr_down_time) + ACK*8 / V_curr + T_SIFS
                    if ACK_down:
                        curr_up_time_alone = max(curr_up_time, curr_down_time) + ACK*8 / V_curr + T_SIFS
                    curr_time = max(curr_down_time_alone, curr_up_time_alone)
                    curr_down_time_alone = curr_time
                    curr_up_time_alone = curr_time

                    curr_down_time_alone += (p_CFPoll_header + downstream[i] + p_FCS)*8 / V_max + T_SIFS
                    curr_up_time_alone += (2 * p_CFPoll_header + 1 + upstream[i] + p_FCS)*8 / V_max + T_SIFS
                    curr_time_alone = max(curr_up_time_alone, curr_down_time_alone)

                    delta_time.append(curr_time_alone - curr_time_concurrent)
                    concurrent_time.append([curr_down_time_concurrent,curr_up_time_concurrent])
                    alone_time.append([curr_down_time_alone, curr_up_time_alone])
                else:
                    # cannot concurrent transmit with last station
                    delta_time.append(0)
                    concurrent_time.append([0, 0])
                    alone_time.append([0, 0])
            # transmit the packet with the information of delta_time
        if last_station == -1 or max(delta_time) <= 0:
            # cannot concurrent transmist with last station
            curr_max_time = max(curr_up_time, curr_down_time)
            if ACK_up:
                curr_down_time = curr_max_time + T_SIFS + ACK*8 / V_curr
                ACK_up = False
            if ACK_down:
                curr_up_time = curr_max_time + T_SIFS + ACK*8 / V_curr
                ACK_down = False
            # transmit the Station's packets with uploading
            last_station = unvisitedStation[0]
            for k in unvisitedStation:
                if upstream[k] > downstream[k]:
                    last_station = k
                    break

            visitedStations.append(last_station)
            unvisitedStation = getUnvisitedStations(visitedStations,len(upstream))
            if not unvisitedStation:
                # transmit the last station's packet and return
                V_curr = V_max
                curr_down_time += (p_CFPoll_header + downstream[last_station] + p_FCS)*8/V_max
                curr_up_time += (2*p_CFPoll_header + 1 + upstream[last_station] + p_FCS)*8/V_max
                if upstream[last_station] > 0:
                    ACK_up = True
                else:
                    ACK_up = False
                if downstream[last_station] > 0:
                    ACK_down = True
                else:
                    ACK_down = False
                return [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr]
            # determine whether concurrent with the next node
            delta_time_forward = []
            concurrent_time_forward = []
            alone_time_forward = []
            for j in unvisitedStation:
                # alone
                curr_time_alone = max(curr_up_time,curr_down_time)
                curr_down_time_alone = curr_time_alone + T_SIFS + (p_CFPoll_header + downstream[last_station] + p_FCS)*8/V_max
                curr_up_time_alone = curr_time_alone + T_SIFS + (2*p_CFPoll_header + upstream[last_station] + p_FCS)*8/V_max
                curr_max_time_alone = max(curr_down_time_alone, curr_up_time_alone)
                if upstream[last_station] > 0:
                    curr_down_time_alone = curr_max_time_alone + T_SIFS + ACK*8/V_max
                if downstream[last_station] > 0:
                    curr_up_time_alone += T_SIFS + ACK*8/V_max

                curr_time_alone = max(curr_down_time_alone, curr_up_time_alone)

                curr_down_time_alone1 = curr_time_alone + T_SIFS + (p_CFPoll_header + downstream[j] + p_FCS)*8 / V_max
                curr_up_time_alone1 = curr_time_alone + T_SIFS + (2*p_CFPoll_header + upstream[j] + p_FCS)*8 / V_max

                curr_time_alone1 = max(curr_down_time_alone1, curr_up_time_alone1)

                # concurrent
                op_rate = lookupRate(matSIR[last_station][j])

                if op_rate == 0:
                    # cannot use concurrent transmission
                    delta_time_forward.append(0)
                    concurrent_time_forward.append([0, 0])
                    continue
                curr_down_time_concurrent = max(curr_down_time, curr_up_time) + T_SIFS + (p_CFPoll_header + downstream[last_station] + p_FCS)*8/op_rate
                curr_up_time_concurrent = max(curr_down_time, curr_up_time) + T_SIFS + (2*p_CFPoll_header + upstream[last_station] + p_FCS)*8/op_rate

                if curr_down_time_concurrent < curr_up_time_concurrent:
                    curr_down_time_concurrent1 = curr_down_time_concurrent + T_SIFS + (p_CFPoll_header + downstream[j] + p_FCS)*8 / op_rate
                    if curr_down_time_concurrent1 >= curr_up_time_concurrent:
                        if upstream[last_station] > 0:
                            curr_down_time_concurrent1 += T_SIFS + ACK*8/op_rate
                    else:
                        if upstream[last_station] > 0:
                            curr_down_time_concurrent1 = max(curr_up_time_concurrent, curr_down_time_concurrent1) + T_SIFS + ACK*8/op_rate

                    if downstream[last_station] > 0:
                        curr_up_time_concurrent1 = curr_up_time_concurrent + T_SIFS + ACK*8/op_rate
                    else:
                        curr_up_time_concurrent1 = max(curr_up_time_concurrent, curr_down_time_concurrent)

                    curr_up_time_concurrent1 += T_SIFS + (p_CFPoll_header + upstream[j] + p_FCS)*8/op_rate

                    curr_time_concurrent = max(curr_down_time_concurrent1, curr_up_time_concurrent1)

                    delta_time_forward.append(curr_time_alone1 - curr_time_concurrent)
                    concurrent_time_forward.append([curr_up_time_concurrent1,curr_down_time_concurrent1])
                    continue

                delta_time_forward.append(0)
                concurrent_time_forward.append([0,0])

            if max(delta_time_forward) <= 0:
                # alone
                curr_down_time = curr_down_time_alone
                curr_up_time = curr_up_time_alone
                ACK_down = False
                ACK_up = False
                V_curr = V_max
            else:
                # concurrent
                index = delta_time_forward.index(max(delta_time_forward))
                V_curr = lookupRate(matSIR[last_station][unvisitedStation[index]])
                last_station = unvisitedStation[index]
                curr_down_time = concurrent_time_forward[index][0]
                curr_up_time = concurrent_time_forward[index][1]
                if upstream[last_station] > 0:
                    ACK_up = True
                else:
                    ACK_up = False
                if downstream[last_station] > 0:
                    ACK_down = True
                else:
                    ACK_down = False
                visitedStations.append(last_station)

        else:
            # transmit the station's packets with the minimal time
            # transmission rate keep unchanged
            last_station_i = delta_time.index(max(delta_time))
            curr_down_time = concurrent_time[last_station_i][0]
            curr_up_time = concurrent_time[last_station_i][1]
            last_station = unvisitedStation[last_station_i]
            if upstream[last_station] > 0:
                ACK_up = True
            else:
                ACK_up = False
            if downstream[last_station] > 0:
                ACK_down = True
            else:
                ACK_down = False
            visitedStations.append(last_station)
        if not unvisitedStation:
            return [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr]


def contention_free_inital_stage_sim(mat_SIR):
    num_stations = len(mat_SIR)
    packet_length_info = 1
    L_probe_packet = p_CFPoll_header + packet_length_info + p_FCS
    L_probe_reply_packet = p_CFPoll_header + packet_length_info + p_FCS

    # simulate the procedure of inital stage
    curr_up_time = 0
    curr_down_time = 0

    curr_down_time = L_probe_packet*8/V_max
    curr_up_time = 0
    for i in range(num_stations):
        if i!=0:
            curr_down_time = curr_up_time_start + p_CFPoll_header*8/V_max
            curr_down_time += L_probe_packet*8/V_max
        # calculate the uploaded packet information
        curr_up_time = max(curr_down_time, curr_up_time)

        L_probe_reply_packet = p_CFPoll_header + packet_length_info + p_FCS
        for j in range(num_stations):
            if i == j:
                continue
            if mat_SIR[i][j] < 20:
                L_probe_reply_packet += 2

        curr_up_time_start = curr_up_time + T_SIFS
        curr_up_time += T_SIFS + L_probe_reply_packet*8/V_max

    return [curr_down_time, curr_up_time]

def greedyPollingWithoutScheduler(matSIR, upstream, downstream, curr_up_time, curr_down_time, last_station, ACK_up=False, ACK_down=False, current_rate = V_max):

    for i in range(len(upstream)):
        # op_rate = lookupRate(matSIR[last_station][i])
        # if op_rate < current_rate or curr_down_time >= curr_up_time:
        #     # cannot use concurrent transmission
        #     curr_max_time = max(curr_down_time, curr_up_time)
        #     if ACK_up:
        #         curr_down_time = curr_max_time + T_SIFS + ACK/V_max
        #     if ACK_down:
        #         curr_up_time = curr_max_time + T_SIFS + ACK/V_max
        #
        #     curr_max_time = max(curr_down_time, curr_up_time)
        #     curr_down_time = curr_max_time + (p_CFPoll_header + downstream[i] + p_FCS)/V_max
        #     curr_up_time = curr_max_time + (2 * p_CFPoll_header + 1 + upstream[i] + p_FCS)/V_max
        #
        #     if downstream[i] > 0:
        #         ACK_down = True
        #     else:
        #         ACK_down = False
        #     if upstream[i] > 0:
        #         ACK_up = True
        #     else:
        #         ACK_up = False
        #     last_station = i
        # else:
        #     # can use concurrent transmission
        #     curr_down_time += (p_CFPoll_header + downstream[i] + p_FCS)/V_max
        #     if ACK_up:
        #         curr_down_time = max(curr_down_time, curr_up_time) + T_SIFS + ACK/V_max
        #
        #     if ACK_down:
        #         curr_up_time += T_SIFS + ACK/V_max
        #     curr_up_time += (2 * p_CFPoll_header + 1 + upstream[i] + p_FCS)/V_max
        #
        #     if downstream[i] > 0:
        #         ACK_down = True
        #     else:
        #         ACK_down = False
        #     if upstream[i] > 0:
        #         ACK_up = True
        #     else:
        #         ACK_up = False
        #     last_station = i
        # cannot use concurrent transmission
        curr_max_time = max(curr_down_time, curr_up_time)
        if ACK_up:
            curr_down_time = curr_max_time + T_SIFS + ACK*8 / V_max
        if ACK_down:
            curr_up_time = curr_max_time + T_SIFS + ACK*8 / V_max

        curr_max_time = max(curr_down_time, curr_up_time)
        curr_down_time = curr_max_time + T_SIFS + (p_CFPoll_header + downstream[i] + p_FCS)*8 / V_max
        curr_up_time = curr_max_time + T_SIFS + (2 * p_CFPoll_header + 1 + upstream[i] + p_FCS)*8 / V_max

        if downstream[i] > 0:
            ACK_down = True
        else:
            ACK_down = False
        if upstream[i] > 0:
            ACK_up = True
        else:
            ACK_up = False
        last_station = i
    return [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, current_rate]

def greedyPolling_upWithFixRate(matSIR, upstream, downstream, curr_up_time, curr_down_time, last_station, ACK_up=False, ACK_down=False, current_rate = V_max):
    V_curr = current_rate
    count = 0
    visitedStations = []
    while(count < len(upstream)):
        unvisitedStation = getUnvisitedStations(visitedStations,len(upstream))
        if not unvisitedStation:
            return [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr]
        delta_time = []
        concurrent_time = []
        alone_time = []
        if last_station != -1:
            for i in unvisitedStation:
                op_rate = lookupRate(matSIR[last_station][i])
                if op_rate >= V_curr:
                    # concurrent: using V_curr as the transmission rate
                    if curr_up_time <= curr_down_time:
                        delta_time.append(0)
                        concurrent_time.append([0,0])
                        alone_time.append([0,0])
                        continue

                    if ACK_down:
                        curr_up_time_concurrent = curr_up_time + T_SIFS + ACK*8/V_max
                    else:
                        curr_up_time_concurrent = max(curr_up_time, curr_down_time)

                    curr_down_time_concurrent = curr_down_time + T_SIFS + (p_CFPoll_header + downstream[i] + p_FCS)*8/V_curr

                    if ACK_up:
                        curr_down_time_concurrent = max(curr_down_time_concurrent, curr_up_time_concurrent) + T_SIFS + ACK*8/V_curr
                        ACK_up_transfered = True
                    curr_up_time_concurrent += T_SIFS + (p_CFPoll_header + 1 + upstream[i] + p_FCS)*8/V_max
                    curr_time_concurrent = max(curr_up_time_concurrent, curr_down_time_concurrent)

                    # alone: using maximal transmission rate as current transmission rate
                    curr_down_time_alone = max(curr_up_time, curr_down_time)
                    curr_up_time_alone = max(curr_up_time, curr_down_time)
                    if ACK_up:
                        curr_down_time_alone = max(curr_up_time, curr_down_time) + ACK*8 / V_curr + T_SIFS
                    if ACK_down:
                        curr_up_time_alone = max(curr_up_time, curr_down_time) + ACK*8 / V_max + T_SIFS
                    curr_time = max(curr_down_time_alone, curr_up_time_alone)
                    curr_down_time_alone = curr_time
                    curr_up_time_alone = curr_time

                    curr_down_time_alone += (p_CFPoll_header + downstream[i] + p_FCS)*8 / V_max + T_SIFS
                    curr_up_time_alone += (2 * p_CFPoll_header + 1 + upstream[i] + p_FCS)*8 / V_max + T_SIFS
                    curr_time_alone = max(curr_up_time_alone, curr_down_time_alone)

                    delta_time.append(curr_time_alone - curr_time_concurrent)
                    concurrent_time.append([curr_down_time_concurrent,curr_up_time_concurrent])
                    alone_time.append([curr_down_time_alone, curr_up_time_alone])
                else:
                    # cannot concurrent transmit with last station
                    delta_time.append(0)
                    concurrent_time.append([0, 0])
                    alone_time.append([0, 0])
            # transmit the packet with the information of delta_time
        if last_station == -1 or max(delta_time) <= 0:
            # cannot concurrent transmist with last station
            curr_max_time = max(curr_up_time, curr_down_time)
            if ACK_up:
                curr_down_time = curr_max_time + T_SIFS + ACK*8 / V_curr
                ACK_up = False
            if ACK_down:
                curr_up_time = curr_max_time + T_SIFS + ACK*8 / V_max
                ACK_down = False
            # transmit the Station's packets with uploading
            last_station = unvisitedStation[0]
            for k in unvisitedStation:
                if upstream[k] > downstream[k]:
                    last_station = k
                    break

            visitedStations.append(last_station)
            unvisitedStation = getUnvisitedStations(visitedStations,len(upstream))
            if not unvisitedStation:
                # transmit the last station's packet and return
                V_curr = V_max
                curr_down_time += (p_CFPoll_header + downstream[last_station] + p_FCS)*8/V_max
                curr_up_time += (2*p_CFPoll_header + 1 + upstream[last_station] + p_FCS)*8/V_max
                if upstream[last_station] > 0:
                    ACK_up = True
                else:
                    ACK_up = False
                if downstream[last_station] > 0:
                    ACK_down = True
                else:
                    ACK_down = False
                return [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr]
            # determine whether concurrent with the next node
            delta_time_forward = []
            concurrent_time_forward = []
            alone_time_forward = []
            for j in unvisitedStation:
                # alone
                curr_time_alone = max(curr_up_time,curr_down_time)
                curr_down_time_alone = curr_time_alone + T_SIFS + (p_CFPoll_header + downstream[last_station] + p_FCS)*8/V_max
                curr_up_time_alone = curr_time_alone + T_SIFS + (2*p_CFPoll_header + upstream[last_station] + p_FCS)*8/V_max
                curr_max_time_alone = max(curr_down_time_alone, curr_up_time_alone)
                if upstream[last_station] > 0:
                    curr_down_time_alone = curr_max_time_alone + T_SIFS + ACK*8/V_max
                if downstream[last_station] > 0:
                    curr_up_time_alone += T_SIFS + ACK*8/V_max

                curr_time_alone = max(curr_down_time_alone, curr_up_time_alone)

                curr_down_time_alone1 = curr_time_alone + T_SIFS + (p_CFPoll_header + downstream[j] + p_FCS)*8 / V_max
                curr_up_time_alone1 = curr_time_alone + T_SIFS + (2*p_CFPoll_header + upstream[j] + p_FCS)*8 / V_max

                curr_time_alone1 = max(curr_down_time_alone1, curr_up_time_alone1)

                # concurrent
                op_rate = lookupRate(matSIR[last_station][j])

                if op_rate == 0:
                    # cannot use concurrent transmission
                    delta_time_forward.append(0)
                    concurrent_time_forward.append([0, 0])
                    continue
                curr_down_time_concurrent = max(curr_down_time, curr_up_time) + T_SIFS + (p_CFPoll_header + downstream[last_station] + p_FCS)*8/op_rate
                curr_up_time_concurrent = max(curr_down_time, curr_up_time) + T_SIFS + (2*p_CFPoll_header + upstream[last_station] + p_FCS)*8/V_max

                if curr_down_time_concurrent < curr_up_time_concurrent:
                    curr_down_time_concurrent1 = curr_down_time_concurrent + T_SIFS + (p_CFPoll_header + downstream[j] + p_FCS)*8 / op_rate
                    if curr_down_time_concurrent1 >= curr_up_time_concurrent:
                        if upstream[last_station] > 0:
                            curr_down_time_concurrent1 += T_SIFS + ACK*8/op_rate
                    else:
                        if upstream[last_station] > 0:
                            curr_down_time_concurrent1 = max(curr_up_time_concurrent, curr_down_time_concurrent1) + T_SIFS + ACK*8/op_rate

                    if downstream[last_station] > 0:
                        curr_up_time_concurrent1 = curr_up_time_concurrent + T_SIFS + ACK*8/V_max
                    else:
                        curr_up_time_concurrent1 = max(curr_up_time_concurrent, curr_down_time_concurrent)

                    curr_up_time_concurrent1 += T_SIFS + (p_CFPoll_header + upstream[j] + p_FCS)*8/V_max

                    curr_time_concurrent = max(curr_down_time_concurrent1, curr_up_time_concurrent1)

                    delta_time_forward.append(curr_time_alone1 - curr_time_concurrent)
                    concurrent_time_forward.append([curr_up_time_concurrent1,curr_down_time_concurrent1])
                    continue

                delta_time_forward.append(0)
                concurrent_time_forward.append([0,0])

            if max(delta_time_forward) <= 0:
                # alone
                curr_down_time = curr_down_time_alone
                curr_up_time = curr_up_time_alone
                ACK_down = False
                ACK_up = False
                V_curr = V_max
            else:
                # concurrent
                index = delta_time_forward.index(max(delta_time_forward))
                V_curr = lookupRate(matSIR[last_station][unvisitedStation[index]])
                last_station = unvisitedStation[index]
                curr_down_time = concurrent_time_forward[index][0]
                curr_up_time = concurrent_time_forward[index][1]
                if upstream[last_station] > 0:
                    ACK_up = True
                else:
                    ACK_up = False
                if downstream[last_station] > 0:
                    ACK_down = True
                else:
                    ACK_down = False
                visitedStations.append(last_station)

        else:
            # transmit the station's packets with the minimal time
            # transmission rate keep unchanged
            last_station_i = delta_time.index(max(delta_time))
            curr_down_time = concurrent_time[last_station_i][0]
            curr_up_time = concurrent_time[last_station_i][1]
            last_station = unvisitedStation[last_station_i]
            if upstream[last_station] > 0:
                ACK_up = True
            else:
                ACK_up = False
            if downstream[last_station] > 0:
                ACK_down = True
            else:
                ACK_down = False
            visitedStations.append(last_station)
        if not unvisitedStation:
            return [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr]

def greedyPolling(matSIR, upstream, downstream, curr_up_time, curr_down_time, last_station, ACK_up=False, ACK_down=False, current_rate = V_max):
    return greedyPolling_upWithFixRate(matSIR, upstream, downstream, curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, current_rate)
