import numpy as np
import pFDMAC
import genToplogy
import trafficHandler
import PCF
import Janus
########################################################################################################################
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
    matSIR[i][i] = 30
# print("####################################################################################################")
# start the test
def test_performance_betweend_different_protocols_different_packet_length():
    throughputOfDifferentTrafficType = []
    delaOfDifferentTrafficType = []
    for i in range(6):
        throughput = []
        delay = []
        Janus_throughput = []
        Janus_delay = []
        PCF_throughput = []
        PCF_delay = []

        for Plength in [64, 128, 256, 512, 1024, 1500]:
            traffic_amount = 0
            count_round = 0
            PCF_timer = 0
            Janus_flag = True
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

                # start Janus simulator
                if Janus_flag:
                    Janus_time = Janus.Janus_sim(upstream,downstream,matSIR,True)
                    Janus_delay.append(Janus_time)
                    Janus_throughput.append(traffic_amount*16/Janus_time)
                    Janus_flag = False
                # start the contention free period
                if j == 0:
                    [curr_down_time,curr_up_time] = pFDMAC.contention_free_inital_stage_sim(matSIR)
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                      upstream,
                                                                                                                      downstream,
                                                                                                                      curr_up_time,
                                                                                                                      curr_down_time,
                                                                                                                      -1,
                                                                                                                      ACK_up=False,
                                                                                                                      ACK_down=False,
                                                                                                                      current_rate=18)
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, current_time=0, need_ACK=False, Vt=18)
                else:
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                      upstream,
                                                                                                                      downstream,
                                                                                                                      curr_up_time,
                                                                                                                      curr_down_time,
                                                                                                                      last_station,
                                                                                                                      ACK_up,
                                                                                                                      ACK_down,
                                                                                                                      current_rate=V_curr)
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, PCF_timer, PCF_ACK, Vt=18)

                count_round += 1
                # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                if max(curr_down_time,curr_up_time) > 10**5:
                    # print('time out!')
                    break


            # record the throughput
            throughput.append(traffic_amount*8 / max(curr_down_time,curr_up_time))
            delay.append(max(curr_down_time,curr_up_time)/count_round)

            PCF_throughput.append(traffic_amount*8/PCF_timer)
            PCF_delay.append(PCF_timer/count_round)
            # if i == 5:
            #     break
        print("Type " + str(i+1) + " throghtput and delay of greedy polling:")
        print(throughput)
        print(Janus_throughput)
        print(PCF_throughput)
        delay = list(np.array(delay)/1000)
        Janus_delay = list(np.array(Janus_delay)/1000)
        PCF_delay = list(np.array(PCF_delay) / 1000)
        print(delay)
        print(Janus_delay)
        print(PCF_delay)

        throughputOfDifferentTrafficType.append([throughput, Janus_throughput, PCF_throughput])
        delaOfDifferentTrafficType.append([delay, Janus_delay, PCF_delay])
    print(throughputOfDifferentTrafficType)
    print(delaOfDifferentTrafficType)
    print("####################################################################################################")

# print("####################################################################################################")
# throughput under different network sizes
# traffic type is saturated and distributed accord with distribution characteristic
def test_performance_betweend_different_protocols_different_saturated_distributed_traffic():
    throughput_with_different_networksizes = []
    delay_with_different_networksizes = []
    for times in range(10):
        pFDMAC_throughput = []
        Janus_throughput = []
        PCF_throughput = []
        pFDMAC_delay = []
        Janus_delay = []
        PCF_delay = []
        for num_stations in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            top_rnd = genToplogy.getRandomTopology([300, 300], num_stations)
            matSIR = np.array(genToplogy.calc_SIR(top_rnd, [150, 150], 100))
            for k in range(len(matSIR)):
                matSIR[k][k] = 30
            traffic_amount = 0
            Janus_flag = True
            count_round = 0
            for j in range(20000):
                upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)

                traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                if Janus_flag:
                    if True:
                        Janus_time = Janus.Janus_sim(upstream, downstream, matSIR, False)
                        Janus_throughput.append(traffic_amount * 8 / Janus_time)
                        Janus_delay.append(Janus_time/1000)
                    else:
                        Janus_time = Janus.Janus_sim(upstream, downstream, matSIR, True)
                        Janus_throughput.append(traffic_amount * 16 / Janus_time)
                        Janus_delay.append(Janus_time/1000)
                    Janus_flag = False
                # start the contention free period
                if j == 0:
                    [curr_down_time,curr_up_time] = pFDMAC.contention_free_inital_stage_sim(matSIR)
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                      upstream,
                                                                                                                      downstream,
                                                                                                                      curr_up_time,
                                                                                                                      curr_down_time,
                                                                                                                      -1,
                                                                                                                      ACK_up=False,
                                                                                                                      ACK_down=False,
                                                                                                                      current_rate=18)
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, current_time=0, need_ACK=False, Vt=18)

                else:
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                      upstream,
                                                                                                                      downstream,
                                                                                                                      curr_up_time,
                                                                                                                      curr_down_time,
                                                                                                                      last_station,
                                                                                                                      ACK_up,
                                                                                                                      ACK_down,
                                                                                                                      current_rate=V_curr)
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, PCF_timer, PCF_ACK, Vt=18)

                count_round +=1
                # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                if max(curr_down_time,curr_up_time) > 10**5:
                    break
            # record the throughput
            pFDMAC_throughput.append(traffic_amount * 8 / max(curr_down_time,curr_up_time))
            PCF_throughput.append(traffic_amount * 8 / PCF_timer)
            pFDMAC_delay.append(max(curr_down_time,curr_up_time)/count_round/1000)
            PCF_delay.append(PCF_timer/count_round/1000)
        throughput_with_different_networksizes.append([pFDMAC_throughput, Janus_throughput, PCF_throughput])
        delay_with_different_networksizes.append([pFDMAC_delay, Janus_delay, PCF_delay])

    print("throghtput(different protocols) with different network sizes:")
    print(throughput_with_different_networksizes)
    print(delay_with_different_networksizes)

########################################################################################################################
########################################################################################################################
# print("####################################################################################################")
# test the performance with different network size
throughput = []
# for num_stations in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
#     tmp = []
#     for times in range(10):
#         top_rnd = genToplogy.getRandomTopology([300,300], num_stations)
#         matSIR = np.array(genToplogy.calc_SIR(top_rnd, [150, 150], 100))
#
#         traffic_amount = 0
#         for j in range(20000):
#             # saturated traffic with different packet length
#             upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)
#
#             traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))
#
#             # start the contention free period
#             if j == 0:
#                 [curr_down_time,curr_up_time] = pFDMAC.contention_free_inital_stage_sim(matSIR)
#                 [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
#                                                                                                                   upstream,
#                                                                                                                   downstream,
#                                                                                                                   curr_up_time,
#                                                                                                                   curr_down_time,
#                                                                                                                   -1,
#                                                                                                                   ACK_up=False,
#                                                                                                                   ACK_down=False,
#                                                                                                                   current_rate=18)
#             else:
#                 [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
#                                                                                                                   upstream,
#                                                                                                                   downstream,
#                                                                                                                   curr_up_time,
#                                                                                                                   curr_down_time,
#                                                                                                                   last_station,
#                                                                                                                   ACK_up,
#                                                                                                                   ACK_down,
#                                                                                                                   current_rate=V_curr)
#             # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
#             if max(curr_down_time,curr_up_time) > 10**5:
#                 # print('time out!')
#                 break
#         # record the throughput
#         tmp.append(traffic_amount / max(curr_down_time,curr_up_time))
#     throughput.append(tmp)

# print("throughput with different network size:")
# print(throughput)
# for i in range(len(throughput)):
#     print(throughput[i])
# print("####################################################################################################")

########################################################################################################################
########################################################################################################################
# #test the performance with scheduler
# throughput = []
# for times in range(1):
#     top_rnd = genToplogy.getRandomTopology([300, 300], 10)
#     matSIR = np.array(genToplogy.calc_SIR(top_rnd, [150, 150], 100))
#
#     traffic_amount = 0
#     for j in range(20000):
#         # saturated traffic with different packet length
#         upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True, 1024)
#         # upstream, downstream = trafficHandler.genAsymmetricTraffic(len(matSIR), False, 1024)
#         traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))
#
#         # start the contention free period
#         if j == 0:
#             [curr_down_time, curr_up_time] = pFDMAC.contention_free_inital_stage_sim(matSIR)
#             [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPollingWithoutScheduler(matSIR,
#                                                                                                               upstream,
#                                                                                                               downstream,
#                                                                                                               curr_up_time,
#                                                                                                               curr_down_time,
#                                                                                                               -1,
#                                                                                                               ACK_up=False,
#                                                                                                               ACK_down=False,
#                                                                                                               current_rate=18)
#         else:
#             [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPollingWithoutScheduler(matSIR,
#                                                                                                               upstream,
#                                                                                                               downstream,
#                                                                                                               curr_up_time,
#                                                                                                               curr_down_time,
#                                                                                                               last_station,
#                                                                                                               ACK_up,
#                                                                                                               ACK_down,
#                                                                                                               current_rate=V_curr)
#         # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
#         if max(curr_down_time, curr_up_time) > 10 ** 5:
#             # print('time out!')
#             break
#     # record the throughput
#     throughput.append(traffic_amount / max(curr_down_time, curr_up_time))
# print("######################################################################################################")
# print("throughput without scheduler:")
# print(throughput)
########################################################################################################################

# print("####################################################################################################")
# scheduler gain
# start the test
def test_scheduler_gain():
    throughput = []
    for times in range(10):
        throughput_w = []
        throughput_wo = []
        for i in range(5):
            throughput_each_traffic_type = []
            throughput_each_traffic_type_wo = []
            for num_stations in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                top_rnd = genToplogy.getRandomTopology([300, 300], num_stations)
                matSIR = np.array(genToplogy.calc_SIR(top_rnd, [150, 150], 100))
                for k in range(len(matSIR)):
                    matSIR[k][k] = 30
                traffic_amount = 0
                for j in range(20000):
                    if i == 0: # saturated traffic with the same packet length
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)
                    elif i == 1: # only downstream, nothing to upload
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 0, True)
                    elif i == 2: # only upstream, nothing to download
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0, 1, True)
                    elif i == 3: # typical asymmetric traffic
                        upstream, downstream = trafficHandler.genAsymmetricTraffic(len(matSIR),True)
                    elif i == 4: # random traffic
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0.5, 0.5, True)

                    traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                    # start the contention free period
                    if j == 0:
                        [curr_down_time,curr_up_time] = pFDMAC.contention_free_inital_stage_sim(matSIR)
                        [curr_up_time1, curr_down_time1, last_station1, ACK_up1, ACK_down1, V_curr1] = pFDMAC.greedyPollingWithoutScheduler(
                                                                                                                        matSIR,
                                                                                                                        upstream,
                                                                                                                        downstream,
                                                                                                                        curr_up_time,
                                                                                                                        curr_down_time,
                                                                                                                        -1,
                                                                                                                        ACK_up=False,
                                                                                                                        ACK_down=False,
                                                                                                                        current_rate=18)

                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                          upstream,
                                                                                                                          downstream,
                                                                                                                          curr_up_time,
                                                                                                                          curr_down_time,
                                                                                                                          -1,
                                                                                                                          ACK_up=False,
                                                                                                                          ACK_down=False,
                                                                                                                          current_rate=18)

                    else:
                        [curr_up_time1, curr_down_time1, last_station1, ACK_up1, ACK_down1, V_curr1] = pFDMAC.greedyPollingWithoutScheduler(
                                                                                                                        matSIR,
                                                                                                                        upstream,
                                                                                                                        downstream,
                                                                                                                        curr_up_time1,
                                                                                                                        curr_down_time1,
                                                                                                                        last_station1,
                                                                                                                        ACK_up1,
                                                                                                                        ACK_down1,
                                                                                                                        current_rate=V_curr1)
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                          upstream,
                                                                                                                          downstream,
                                                                                                                          curr_up_time,
                                                                                                                          curr_down_time,
                                                                                                                          last_station,
                                                                                                                          ACK_up,
                                                                                                                          ACK_down,
                                                                                                                          current_rate=V_curr)


                    # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                    if max(curr_down_time,curr_up_time) > 10**5:
                        # print('time out!')
                        break
                # record the throughput
                throughput_each_traffic_type.append(traffic_amount*8 / max(curr_down_time,curr_up_time))
                throughput_each_traffic_type_wo.append(traffic_amount*8 / max(curr_down_time1, curr_up_time1))

            throughput_w.append(throughput_each_traffic_type)
            throughput_wo.append(throughput_each_traffic_type_wo)
        throughput.append([throughput_w, throughput_wo])
    print("throghtput(with/without scheduler) of greedy polling:")
    print(throughput)
    print("####################################################################################################")
########################################################################################################################
# the parameter's influence on pFDMAC, contention-free period
########################################################################################################################
# throughput with different contention-free period
# traffic type is saturated and distributed accord with distribution characteristic
def test_throughput_with_different_CFP(CFP_list = [0.2, 0.5, 1, 2, 4]):
    print("start the test: throughput with different contention-free period")
    throughput_with_different_CFP= []
    for CFP in CFP_list:
        for times in range(10):
            pFDMAC_throughput = []
            for num_stations in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                top_rnd = genToplogy.getRandomTopology([300, 300], num_stations)
                matSIR = np.array(genToplogy.calc_SIR(top_rnd, [150, 150], 100))
                for k in range(len(matSIR)):
                    matSIR[k][k] = 30
                traffic_amount = 0
                for j in range(20000):
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)

                    traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                    # start the contention free period
                    if j == 0:
                        [curr_down_time,curr_up_time] = pFDMAC.contention_free_inital_stage_sim(matSIR)
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                          upstream,
                                                                                                                          downstream,
                                                                                                                          curr_up_time,
                                                                                                                          curr_down_time,
                                                                                                                          -1,
                                                                                                                          ACK_up=False,
                                                                                                                          ACK_down=False,
                                                                                                                          current_rate=18)
                    else:
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, V_curr] = pFDMAC.greedyPolling(matSIR,
                                                                                                                          upstream,
                                                                                                                          downstream,
                                                                                                                          curr_up_time,
                                                                                                                          curr_down_time,
                                                                                                                          last_station,
                                                                                                                          ACK_up,
                                                                                                                          ACK_down,
                                                                                                                          current_rate=V_curr)
                    # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                    if max(curr_down_time,curr_up_time) > CFP * 10**5:
                        break
                # record the throughput
                pFDMAC_throughput.append(traffic_amount * 8 / max(curr_down_time,curr_up_time))
            if times == 0:
                array_pFDMAC_throughput = np.array(pFDMAC_throughput)
            else:
                array_pFDMAC_throughput += np.array(pFDMAC_throughput)
        throughput_with_different_CFP.append(array_pFDMAC_throughput/10)
    throughput_with_different_CFP = np.array(throughput_with_different_CFP)
    print("throghtput(different protocols) with different Contetion-free period:")
    print(throughput_with_different_CFP.tolist())

    print("End the test: throughput with different contention-free period")
    print("####################################################################################################")


# test_throughput_with_different_CFP()
test_performance_betweend_different_protocols_different_packet_length()
