import numpy as np
import pFHMAC
import PCF
import genToplogy
import trafficHandler

########################################################################################################################
numOfstations_list = np.arange(5, 55, 5)
numOfstations_list1 = np.arange(10, 110, 20)

########################################################################################################################
# test the performance with different traffic types and different packet length
# the toplology is random distributed and network size is 10
# type 1-5 upstream and the downstream with the same packet length
# type 6 is the saturated traffic with different packet lengths.

# obtain the typical topology's SIR map
top_rnd_10 = np.array([[59, 298],
                      [241, 76],
                      [7, 104],
                      [162, 236],
                      [246, 160],
                      [63, 227],
                      [42, 41],
                      [153, 28],
                      [10, 62],
                      [154, 15]])
matSIR = np.array(genToplogy.calc_SIR(top_rnd_10, [150, 150], 100))
for i in range(len(matSIR)):
    matSIR[i][i] = 0

def genMatSIR(num_station):
    # generate a topology consists of num_station stations
    stations_pos = np.array(genToplogy.rnd_top_square(num_node=num_station))
    matSIR = np.array(genToplogy.calc_SIR(stations_pos, [150, 150], 100))

    for i in range(len(matSIR)):
        matSIR[i][i] = 0

    return matSIR
def makeAllFullDuplex(matSIR):
    AllmatSIR = matSIR.copy()
    for i in range(len(AllmatSIR)):
        AllmatSIR[i][i] = 30
    return AllmatSIR
# print("####################################################################################################")
# start the test
def test_performance_with_saturated_traffic():
    throughput = []
    delay = []
    ALL_throughput = []
    ALL_delay = []
    PCF_throughput = []
    PCF_delay = []
    for numStation in numOfstations_list:
        matSIR = genMatSIR(numStation)
        all_matSIR = makeAllFullDuplex(matSIR)
        traffic_amount = 0
        count_round = 0

        for j in range(20000):
            # saturated traffic with different packet length
            upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True, 1024)
            traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

            # start the contention free period
            if j == 0:
                [curr_down_time, curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down] = pFHMAC.greedyPolling(matSIR,
                                                                                                      upstream,
                                                                                                      downstream,
                                                                                                      curr_up_time,
                                                                                                      curr_down_time,
                                                                                                      [-1, -1],
                                                                                                      np.zeros((len(
                                                                                                          matSIR),),
                                                                                                               dtype=np.int32),
                                                                                                      np.zeros((len(
                                                                                                          matSIR),),
                                                                                                               dtype=np.int32))

                [curr_down_time1, curr_up_time1] = pFHMAC.contention_free_inital_stage_sim(all_matSIR)
                [curr_up_time1, curr_down_time1, last_station1, ACK_up1, ACK_down1] = pFHMAC.greedyPolling(all_matSIR,
                                                                                                      upstream,
                                                                                                      downstream,
                                                                                                      curr_up_time1,
                                                                                                      curr_down_time1,
                                                                                                      [-1, -1],
                                                                                                      np.zeros((len(
                                                                                                          all_matSIR),),
                                                                                                          dtype=np.int32),
                                                                                                      np.zeros((len(
                                                                                                          all_matSIR),),
                                                                                                          dtype=np.int32))

                [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, current_time=0, need_ACK=False, Vt=18)
            else:
                [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down] = pFHMAC.greedyPolling(matSIR,
                                                                                                      upstream,
                                                                                                      downstream,
                                                                                                      curr_up_time,
                                                                                                      curr_down_time,
                                                                                                      last_station,
                                                                                                      ACK_up,
                                                                                                      ACK_down)

                [curr_up_time1, curr_down_time1, last_station1, ACK_up1, ACK_down1] = pFHMAC.greedyPolling(all_matSIR,
                                                                                                           upstream,
                                                                                                           downstream,
                                                                                                           curr_up_time1,
                                                                                                           curr_down_time1,
                                                                                                           last_station1,
                                                                                                           ACK_up1,
                                                                                                           ACK_down1)
                [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, PCF_timer, PCF_ACK, Vt=18)

            count_round += 1
            # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
            if max(curr_down_time, curr_up_time) > 10 ** 5:
                # print('time out!')
                break

        # record the throughput
        throughput.append(traffic_amount * 8 / max(curr_down_time, curr_up_time))
        PCF_throughput.append(traffic_amount*8/PCF_timer)
        ALL_throughput.append(traffic_amount*8/max(curr_down_time1, curr_up_time1))

        delay.append(max(curr_down_time, curr_up_time) / count_round)
        PCF_delay.append(PCF_timer/count_round)
        ALL_delay.append(max(curr_up_time1,curr_down_time1) / count_round)

    delay = list(np.array(delay) / 1000)
    PCF_delay = list(np.array(PCF_delay) / 1000)
    ALL_delay = list(np.array(ALL_delay) / 1000)
    # print(throughput)
    # print(delay)

    return [ALL_throughput, throughput, PCF_throughput], [ALL_delay, delay,PCF_delay]

def test_performance_with_saturated_traffic_50times():
    throughput, delay = test_performance_with_saturated_traffic()
    throughput_sum = np.array(throughput)
    delay_sum = np.array(delay)

    for i in range(0,49):
        throughput, delay = test_performance_with_saturated_traffic()

        throughput_sum += np.array(throughput)
        delay_sum += np.array(delay)

    print((throughput_sum/50).tolist())
    print((delay_sum/50).tolist())

def test_throughput_with_different_pakcetLength():
    print("hello")

def test_performance_betweend_different_protocols_different_packet_length():
    throughputOfDifferentTrafficType = []
    delaOfDifferentTrafficType = []
    for i in range(6):
        throughput = []
        delay = []
        PCF_throughput = []
        PCF_delay = []
        for Plength in [64, 128, 256, 512, 1024]:
            traffic_amount = 0
            count_round = 0

            for j in range(20000):
                if i == 0: # saturated traffic with the same packet length
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, False, Plength)
                elif i == 1: # only upstream, nothing to download
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 0, False, Plength)
                elif i == 2: # only downstream, nothing to upload
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0, 1, False, Plength)
                elif i == 3: # typical asymmetric traffic
                    upstream, downstream = trafficHandler.genAsymmetricTraffic(len(matSIR),False,Plength)
                elif i == 4: # random traffic
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0.5, 0.5, False, Plength)
                elif i == 5: # saturated traffic with different packet length
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True, 1024)

                traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                # start the contention free period
                if j == 0:
                    [curr_down_time,curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down] = pFHMAC.greedyPolling(matSIR,
                                                                                                                      upstream,
                                                                                                                      downstream,
                                                                                                                      curr_up_time,
                                                                                                                      curr_down_time,
                                                                                                                      [-1,-1],
                                                                                                                      np.zeros((len(matSIR),),dtype=np.int32),
                                                                                                                      np.zeros((len(matSIR),),dtype=np.int32))
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, current_time=0, need_ACK=False, Vt=18)
                else:
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down] = pFHMAC.greedyPolling(matSIR,
                                                                                                                      upstream,
                                                                                                                      downstream,
                                                                                                                      curr_up_time,
                                                                                                                      curr_down_time,
                                                                                                                      last_station,
                                                                                                                      ACK_up,
                                                                                                                      ACK_down)
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, PCF_timer, PCF_ACK, Vt=18)
                count_round += 1
                # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                if max(curr_down_time,curr_up_time) > 10**5:
                    # print('time out!')
                    break


            # record the throughput
            throughput.append(traffic_amount*8 / max(curr_down_time,curr_up_time))
            delay.append(max(curr_down_time,curr_up_time)/count_round)
            PCF_throughput.append(traffic_amount * 8 / PCF_timer)
            PCF_delay.append(PCF_timer/count_round)

        print("Type " + str(i+1) + " throghtput and delay of greedy polling:")
        # print(throughput)
        delay = list(np.array(delay)/1000)
        PCF_delay = list(np.array(PCF_delay) / 1000)
        # print(delay)

        throughputOfDifferentTrafficType.append([throughput, PCF_throughput])
        delaOfDifferentTrafficType.append([delay, PCF_delay])
    print(throughputOfDifferentTrafficType)
    print(delaOfDifferentTrafficType)
    print("####################################################################################################")

def test_throughput_with_different_CFP(CFP_list = [0.2, 0.5, 1, 2, 4]):
    print("start the test: throughput with different contention-free period")
    throughput_with_different_CFP= []
    for CFP in CFP_list:
        test_times = 20
        for times in range(test_times):
            pFHMAC_throughput = []
            for num_stations in numOfstations_list1:
                matSIR = genMatSIR(num_stations)

                traffic_amount = 0
                for j in range(20000):
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)

                    traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                    # start the contention free period
                    if j == 0:
                        [curr_down_time, curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down] = pFHMAC.greedyPolling(matSIR,
                                                                                                              upstream,
                                                                                                              downstream,
                                                                                                              curr_up_time,
                                                                                                              curr_down_time,
                                                                                                              [-1, -1],
                                                                                                              np.zeros((
                                                                                                                       len(
                                                                                                                           matSIR),),
                                                                                                                       dtype=np.int32),
                                                                                                              np.zeros((
                                                                                                                       len(
                                                                                                                           matSIR),),
                                                                                                                       dtype=np.int32))
                    else:
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down] = pFHMAC.greedyPolling(matSIR,
                                                                                                              upstream,
                                                                                                              downstream,
                                                                                                              curr_up_time,
                                                                                                              curr_down_time,
                                                                                                              last_station,
                                                                                                              ACK_up,
                                                                                                              ACK_down)
                    # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                    if max(curr_down_time,curr_up_time) > CFP * 10**5:
                        break
                # record the throughput
                pFHMAC_throughput.append(traffic_amount * 8 / max(curr_down_time,curr_up_time))
            if times == 0:
                array_pFDMAC_throughput = np.array(pFHMAC_throughput)
            else:
                array_pFDMAC_throughput += np.array(pFHMAC_throughput)
        throughput_with_different_CFP.append(array_pFDMAC_throughput/test_times)
    throughput_with_different_CFP = np.array(throughput_with_different_CFP)
    print("throghtput(different protocols) with different Contetion-free period:")
    print(throughput_with_different_CFP.tolist())

    print("End the test: throughput with different contention-free period")
    print("####################################################################################################")

test_performance_with_saturated_traffic_50times()
# test_performance_betweend_different_protocols_different_packet_length()
# test_throughput_with_different_CFP()
