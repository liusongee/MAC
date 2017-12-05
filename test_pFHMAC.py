import numpy as np
import pFHMAC
import PCF
import Janus
import genToplogy
import trafficHandler
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import xlwt
########################################################################################################################
wb = xlwt.Workbook()
ws1 = wb.add_sheet('throughput1')
ws2 = wb.add_sheet('delay1')
ws3 = wb.add_sheet('throughput2')
ws4 = wb.add_sheet('delay2')
ws5 = wb.add_sheet('throughput3')
ws6 = wb.add_sheet('delay3')
ws_line = 0
def write2xls(data, line_num, flag = 1):
    size = np.size(data)
    if not bool(flag - 1):
        for col_num in range(size):
            ws1.write(line_num,col_num,float(data[col_num]))
    elif not bool(flag - 2):
        for col_num in range(size):
            ws2.write(line_num, col_num, float(data[col_num]))
    elif not bool(flag - 3):
        for col_num in range(size):
            ws3.write(line_num, col_num, float(data[col_num]))
    elif not bool(flag - 4):
        for col_num in range(size):
            ws4.write(line_num, col_num, float(data[col_num]))
    elif not bool(flag - 5):
        for col_num in range(size):
            ws5.write(line_num, col_num, float(data[col_num]))
    elif not bool(flag - 6):
        for col_num in range(size):
            ws6.write(line_num, col_num, float(data[col_num]))

########################################################################################################################
numOfstations_list = np.arange(5, 105, 5)
numOfstations_list1 = np.arange(10, 110, 20)
deltaPower = range(-20, 35, 5)
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
AP_pos = [150, 150]
# print(np.shape(top_rnd_10))
# matSIR = np.array(genToplogy.calc_SIR(top_rnd_10, AP_pos, 100))
# matSIR_directional = np.array(genToplogy.calc_SIR_directional(top_rnd_10, AP_pos))
# for i in range(len(matSIR)):
#     matSIR[i][i] = 0
#     matSIR_directional[i][i] = 0
#
# print(matSIR.tolist())
# print(matSIR_directional.tolist())

def vector2Angle(vPos):
    if vPos[0] == 0:
        if vPos[1] > 0:
            return 90
        else:
            return -90
    else:
        return math.atan(vPos[1]/vPos[0])/math.pi*180

def plotTop(pos):
    sectorAngle = 30
    pos = np.array(genToplogy.rnd_top_square(20))
    AP_pos = [300,150]
    # plt.style.use('ggplot')
    fig,ax = plt.subplots()
    # fig.set_size_inches(5,5)
    patches = []
    for i in range(len(pos)):
        angle = vector2Angle([pos[i][0]-AP_pos[0], pos[i][1]-AP_pos[1]])
        if pos[i][0]-AP_pos[0] > 0:
            angle = angle + 180
        patches += [Wedge((pos[i][0],pos[i][1]), 300, angle-sectorAngle/2, angle +sectorAngle/2)] # Full sector

    colors = 100 * np.random.rand(len(patches))
    p = PatchCollection(patches, alpha=0.2)
    p.set_array(np.array(colors))
    ax.add_collection(p)

    ax.scatter(pos[:, 0],pos[:, 1],s=200, alpha=0.6)
    ax.scatter(AP_pos[0], AP_pos[1], s=400)
    # ax.text(150, 150, 'AP', fontsize=15)
    # for i in range(len(pos)):
    #     ax.text(pos[i][0],pos[i][1],str(i+1),fontsize=15)

    plt.xticks(np.arange(0, 330, 30))
    plt.yticks(np.arange(0, 330, 30))
    plt.xlim(0, 300)
    plt.ylim(0, 300)
    plt.show()

def genMatSIR(stations_pos, deltaPower = 10):
    # generate a topology consists of num_station stations
    # stations_pos = np.array(genToplogy.rnd_top_square(num_node=num_station))
    matSIR = np.array(genToplogy.calc_SIR(stations_pos, AP_pos,deltaPower=deltaPower,signalPower=120))

    for i in range(len(matSIR)):
        matSIR[i][i] = 0
    return matSIR

def genMatSIR_directional(stations_pos, ap_pos = AP_pos, deltaPower = 0, angle = np.pi/6):
    # generate a topology consists of num_station stations
    # stations_pos = np.array(genToplogy.rnd_top_square(num_node=num_station))
    matSIR_directional = np.array(genToplogy.calc_SIR_directional(stations_pos, ap_pos, deltaPower=deltaPower,angle=angle))

    for i in range(len(matSIR_directional)):
        matSIR_directional[i][i] = 0
    return matSIR_directional

def makeAllFullDuplex(matSIR):
    # AllmatSIR = matSIR.copy()
    for i in range(len(matSIR)):
        matSIR[i][i] = 30
    return matSIR

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
        stations_pos = np.array(genToplogy.rnd_top_square(num_node=numStation))
        matSIR = genMatSIR(stations_pos)
        all_matSIR = genMatSIR_directional(stations_pos)
        # print(matSIR.tolist())
        # print(all_matSIR.tolist())
        traffic_amount = 0
        count_round = 0

        for j in range(20000):
            # saturated traffic with different packet length
            upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True, 1024)
            traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

            # start the contention free period
            if j == 0:
                [curr_down_time, curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
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
                [curr_up_time1, curr_down_time1, last_station1, ACK_up1, ACK_down1, oRateL, LDpay] = pFHMAC.greedyPolling(all_matSIR,
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
                                                                                                          dtype=np.int32), oRateL, LDpay)

                [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, current_time=0, need_ACK=False, Vt=18)
            else:
                [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
                                                                                                      upstream,
                                                                                                      downstream,
                                                                                                      curr_up_time,
                                                                                                      curr_down_time,
                                                                                                      last_station,
                                                                                                      ACK_up,
                                                                                                      ACK_down)

                [curr_up_time1, curr_down_time1, last_station1, ACK_up1, ACK_down1, oRateL, LDpay] = pFHMAC.greedyPolling(all_matSIR,
                                                                                                           upstream,
                                                                                                           downstream,
                                                                                                           curr_up_time1,
                                                                                                           curr_down_time1,
                                                                                                           last_station1,
                                                                                                           ACK_up1,
                                                                                                           ACK_down1, oRateL, LDpay)
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

    global ws_line
    write2xls(ALL_throughput,ws_line,1)
    write2xls(ALL_delay, ws_line, 2)
    write2xls(throughput, ws_line, 3)
    write2xls(delay, ws_line, 4)
    write2xls(PCF_throughput, ws_line, 5)
    write2xls(PCF_delay, ws_line, 6)
    ws_line += 1

    return [ALL_throughput, throughput, PCF_throughput], [ALL_delay, delay, PCF_delay]

def test_performance_with_saturated_traffic_50times():
    throughput, delay = test_performance_with_saturated_traffic()
    throughput_sum = np.array(throughput)
    delay_sum = np.array(delay)

    for i in range(0,49):
        throughput, delay = test_performance_with_saturated_traffic()

        throughput_sum += np.array(throughput)
        delay_sum += np.array(delay)
    throughput_ave = throughput_sum/50
    delay_ave = delay_sum/50
    print((throughput_sum/50).tolist())
    print((delay_sum/50).tolist())

    global ws_line
    ws_line += 3
    write2xls(throughput_ave[0], ws_line, 1)
    write2xls(delay_ave[0], ws_line, 2)
    write2xls(throughput_ave[1], ws_line, 3)
    write2xls(delay_ave[1], ws_line, 4)
    write2xls(throughput_ave[2], ws_line, 5)
    write2xls(delay_ave[2], ws_line, 6)

def test_APPower_with_saturated_traffic():
    deltaPower = [-20, -10, 0, 10, 20, 30]
    throughput = []
    delay = []

    for numStation in numOfstations_list:
        throughput_deltaP = []
        delay_deltaP = []
        stations_pos = np.array(genToplogy.rnd_top_square(num_node=numStation))
        for dp in deltaPower:
            # matSIR = genMatSIR(stations_pos,dp)
            matSIR = genMatSIR_directional(stations_pos,AP_pos,dp)
            # print(matSIR)
            traffic_amount = 0
            count_round = 0
            for j in range(20000):
                # saturated traffic with different packet length
                upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True, 1024)
                traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                # start the contention free period
                if j == 0:
                    [curr_down_time, curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
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
                else:
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
                                                                                                          upstream,
                                                                                                          downstream,
                                                                                                          curr_up_time,
                                                                                                          curr_down_time,
                                                                                                          last_station,
                                                                                                          ACK_up,
                                                                                                          ACK_down, oRateL, LDpay)

                count_round += 1
                # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                if max(curr_down_time, curr_up_time) > 10 ** 5:
                    # print('time out!')
                    break

            # record the throughput
            throughput_deltaP.append(traffic_amount * 8 / max(curr_down_time, curr_up_time))
            delay_deltaP.append(max(curr_down_time, curr_up_time) / count_round)
        throughput.append(throughput_deltaP)
        delay.append(delay_deltaP)
    delay = list(np.array(delay) / 1000)
    # print(throughput, delay)
    throughput = np.transpose(np.array(throughput)).tolist()
    delay = np.transpose(np.array(delay)).tolist()
    return throughput, delay

def test_APPower_with_traffic():
    throughput = []
    delay = []
    for flag in [True, False]:
        throughput_tr = []
        delay_tr = []
        for tr in range(5):
            stations_pos = np.array(genToplogy.rnd_top_square(num_node=20))
            throughput_deltaP = []
            delay_deltaP = []
            for dp in deltaPower:
                matSIR = genMatSIR(stations_pos,dp)
                if flag:
                    matSIR = makeAllFullDuplex(matSIR)
                # matSIR = genMatSIR_directional(stations_pos,AP_pos,dp)
                # print(matSIR)
                traffic_amount = 0
                count_round = 0
                for j in range(20000):
                    # saturated traffic with different packet length
                    if tr == 0:  # saturated traffic with the same packet length
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)
                    elif tr == 1:  # only upstream, nothing to download
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 0, True)
                    elif tr == 2:  # only downstream, nothing to upload
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0, 1, True)
                    elif tr == 3:  # typical asymmetric traffic
                        upstream, downstream = trafficHandler.genAsymmetricTraffic(len(matSIR), True)
                    elif tr == 4:  # random traffic
                        upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0.5, 0.5, True)

                    traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                    # start the contention free period
                    if not j:
                        [curr_down_time, curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
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
                    else:
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
                                                                                                              upstream,
                                                                                                              downstream,
                                                                                                              curr_up_time,
                                                                                                              curr_down_time,
                                                                                                              last_station,
                                                                                                              ACK_up,
                                                                                                              ACK_down, oRateL, LDpay)

                    count_round += 1
                    # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                    if max(curr_down_time, curr_up_time) > 10 ** 5:
                        # print('time out!')
                        break

                # record the throughput
                throughput_deltaP.append(traffic_amount * 8 / max(curr_down_time, curr_up_time))
                delay_deltaP.append(max(curr_down_time, curr_up_time) / count_round)
            throughput_tr.append(throughput_deltaP)
            delay_tr.append(delay_deltaP)
        throughput.append(throughput_tr)
        delay.append(delay_tr)
    delay = list(np.array(delay) / 1000) # us->ms
    # print(throughput, delay)
    return throughput, delay

def test_deltaPower_50times():
    times = 50
    throughput, delay = test_APPower_with_traffic()
    throughput_sum = np.array(throughput)
    delay_sum = np.array(delay)

    global ws_line
    for i in range(1,times):
        throughput, delay = test_APPower_with_traffic()

        throughput_sum += np.array(throughput)
        delay_sum += np.array(delay)

    throughput_ave = throughput_sum/times
    delay_ave = delay_sum/times

    print((throughput_ave).tolist())
    print((delay_ave).tolist())

    for i in range(2):
        ws_line = 0
        for j in range(5):
            write2xls(throughput_ave[i][j], ws_line, i+1)
            write2xls(delay_ave[i][j], ws_line, i+3)
            ws_line += 1

def test_different_trafficType():
    throughput = []
    delay = []

    for i in range(5):
        throughput_t = []
        delay_t = []
        for numStation in numOfstations_list:
            stations_pos = np.array(genToplogy.rnd_top_square(num_node=numStation))
            matSIR = genMatSIR(stations_pos)
            # matSIR = makeAllFullDuplex(matSIR)
            # matSIR = genMatSIR_directional(stations_pos,AP_pos)
            # print(matSIR)
            traffic_amount = 0
            count_round = 0
            for j in range(20000):
                # saturated traffic with different packet length
                if i == 0: # saturated traffic with the same packet length
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)
                elif i == 1: # only upstream, nothing to download
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 0, True)
                elif i == 2: # only downstream, nothing to upload
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0, 1, True)
                elif i == 3: # typical asymmetric traffic
                    upstream, downstream = trafficHandler.genAsymmetricTraffic(len(matSIR), True)
                elif i == 4: # random traffic
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0.5, 0.5, True)
                traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                # start the contention free period
                if j == 0:
                    [curr_down_time, curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
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
                else:
                    [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
                                                                                                          upstream,
                                                                                                          downstream,
                                                                                                          curr_up_time,
                                                                                                          curr_down_time,
                                                                                                          last_station,
                                                                                                          ACK_up,
                                                                                                          ACK_down, oRateL, LDpay)

                count_round += 1
                # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                if max(curr_down_time, curr_up_time) > 10 ** 5:
                    # print('time out!')
                    break

            # record the throughput
            throughput_t.append(traffic_amount * 8 / max(curr_down_time, curr_up_time))
            delay_t.append(max(curr_down_time, curr_up_time) / count_round)
        throughput.append(throughput_t)
        delay.append(delay_t)
    tmp1 = np.array(delay) / 1000
    delay = tmp1.tolist()
    # print(throughput, delay)
    return throughput, delay

def test_trafficType_50times():
    throughput, delay = test_different_trafficType()
    throughput_sum = np.array(throughput)
    delay_sum = np.array(delay)

    global ws_line
    write2xls(throughput[0], ws_line, 1)
    write2xls(throughput[1], ws_line, 2)
    write2xls(throughput[2], ws_line, 3)
    write2xls(throughput[3], ws_line, 4)
    write2xls(throughput[4], ws_line, 5)
    # write2xls(throughput[5], ws_line, 6)
    ws_line += 1

    for i in range(0, 49):
        throughput, delay = test_different_trafficType()

        write2xls(throughput[0], ws_line, 1)
        write2xls(throughput[1], ws_line, 2)
        write2xls(throughput[2], ws_line, 3)
        write2xls(throughput[3], ws_line, 4)
        write2xls(throughput[4], ws_line, 5)
        # write2xls(throughput[5], ws_line, 6)
        ws_line += 1

        throughput_sum += np.array(throughput)
        delay_sum += np.array(delay)

    throughput_ave = throughput_sum / 50
    delay_ave = delay_sum / 50

    ws_line += 2
    write2xls(throughput_ave[0], ws_line, 1)
    write2xls(throughput_ave[1], ws_line, 2)
    write2xls(throughput_ave[2], ws_line, 3)
    write2xls(throughput_ave[3], ws_line, 4)
    write2xls(throughput_ave[4], ws_line, 5)
    ws_line = 0
    for i in range(5):
        write2xls(delay_ave[i], ws_line, 6)
        ws_line += 1

    print((throughput_sum / 50).tolist())
    print((delay_sum / 50).tolist())

def test_throughput_with_different_CFP(CFP_list = [0.2, 0.5, 1, 2, 4]):
    print("start the test: throughput with different contention-free period")
    throughput_with_different_CFP= []
    for CFP in CFP_list:
        ws_line = 0
        test_times = 500
        for times in range(test_times):
            pFHMAC_throughput = []
            for num_stations in numOfstations_list:
                stations_pos = np.array(genToplogy.rnd_top_square(num_node=num_stations))
                matSIR = genMatSIR(stations_pos)
                traffic_amount = 0
                for j in range(20000):
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)
                    traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))
                    # start the contention free period
                    if j == 0:
                        [curr_down_time, curr_up_time] = pFHMAC.contention_free_inital_stage_sim(matSIR)
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
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
                        [curr_up_time, curr_down_time, last_station, ACK_up, ACK_down, oRateL, LDpay] = pFHMAC.greedyPolling(matSIR,
                                                                                                              upstream,
                                                                                                              downstream,
                                                                                                              curr_up_time,
                                                                                                              curr_down_time,
                                                                                                              last_station,
                                                                                                              ACK_up,
                                                                                                              ACK_down, oRateL, LDpay)
                    # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                    if max(curr_down_time,curr_up_time) > CFP * 10**5:
                        break
                # record the throughput
                pFHMAC_throughput.append(traffic_amount * 8 / max(curr_down_time,curr_up_time))
            write2xls(pFHMAC_throughput, ws_line, CFP_list.index(CFP) + 1)
            ws_line += 1
            if times == 0:
                array_pFDMAC_throughput = np.array(pFHMAC_throughput)
            else:
                array_pFDMAC_throughput += np.array(pFHMAC_throughput)
        throughput_with_different_CFP.append(array_pFDMAC_throughput/test_times)
        ws_line += 2
        write2xls(array_pFDMAC_throughput/test_times, ws_line, CFP_list.index(CFP) + 1)
    throughput_with_different_CFP = np.array(throughput_with_different_CFP)
    print("throghtput(different protocols) with different Contetion-free period:")
    print(throughput_with_different_CFP.tolist())

    print("End the test: throughput with different contention-free period")
    print("####################################################################################################")

def test_deltaPower_decreaseInterference():
    oOppo = []
    deltaPower = [-20, -10, 0, 10, 20, 30]
    for dp in deltaPower:
        oOppo_delta = []
        for numStation in numOfstations_list:
            stations_pos = np.array(genToplogy.rnd_top_square(num_node=numStation))
            allFullOpportunities = numStation * (numStation - 1)
            SIRMat = genMatSIR(stations_pos,dp)

            oSIR_num = np.sum(np.array(SIRMat > 19.6).astype(np.int8)) / allFullOpportunities
            oOppo_delta.append(oSIR_num)
        oOppo.append(oOppo_delta)
    return oOppo

def test_50times():
    oOppo = test_deltaPower_decreaseInterference()
    tmp1 = np.array(oOppo)

    for i in range(29):
        oOppo = test_deltaPower_decreaseInterference()
        tmp1 += np.array(oOppo)
    tmp1 /= 30

    print(tmp1.tolist())

def test_directionalAntenna_decreaseInterference():
    oOppo = []
    DOppo = []
    for numStation in numOfstations_list:
        stations_pos = np.array(genToplogy.rnd_top_square(num_node=numStation))

        allFullOpportunities = numStation * (numStation - 1)
        SIRMat = genMatSIR(stations_pos)
        DSIRMat = genMatSIR_directional(stations_pos)

        oSIR_num = np.sum(np.array(SIRMat > 19.6).astype(np.int8)) / allFullOpportunities
        DSIRMat_num = np.sum(np.array(DSIRMat > 19.6).astype(np.int8)) / allFullOpportunities

        oOppo.append(oSIR_num)
        DOppo.append(DSIRMat_num)
    return  oOppo, DOppo
def test_Interference_50times():
    oOppo, dOppo = test_directionalAntenna_decreaseInterference()
    tmp1 = np.array(oOppo)
    tmp2 = np.array(dOppo)

    for i in range(49):
        oOppo, dOppo = test_directionalAntenna_decreaseInterference()
        tmp1 += np.array(oOppo)
        tmp2 += np.array(dOppo)
    tmp1 = tmp1/50
    tmp2 = tmp2/50

    print(tmp1.tolist(), tmp2.tolist())

def test_Janus_trafficType():
    # in this test program, the Janus exchange period will be discussed and test the throughput under different traffic.
    throughput = []
    delay = []
    for i in range(5):
        throughput_t = []
        delay_t = []
        for numStation in numOfstations_list:
            stations_pos = np.array(genToplogy.rnd_top_square(num_node=numStation))
            matSIR = genMatSIR(stations_pos)
            matSIR = makeAllFullDuplex(matSIR)
            traffic_amount = 0
            count = 0
            overhead_time = 0
            for j in range(2000):
                if i == 0: # saturated traffic with the same packet length
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)
                elif i == 1: # only upstream, nothing to download
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 0, True)
                elif i == 2: # only downstream, nothing to upload
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0, 1, True)
                elif i == 3: # typical asymmetric traffic
                    upstream, downstream = trafficHandler.genAsymmetricTraffic(len(matSIR), True)
                elif i == 4: # random traffic
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0.5, 0.5, True)

                traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))
                count += 1
                # start the contention free period
                if j == 0:
                    start_time = Janus.Janus_sim_overhead(upstream, downstream)
                    overhead_time += start_time
                    [curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length] \
                        = Janus.Janus_sim_exchange_period(upstream, downstream,matSIR,start_time,start_time)
                else:
                    deltaScheduleTime = Janus.add2schedulingTime(upstream, downstream)
                    overhead_time += deltaScheduleTime
                    curr_up_time += deltaScheduleTime
                    curr_down_time += deltaScheduleTime
                    [curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length] \
                        = Janus.Janus_sim_exchange_period(upstream, downstream, matSIR,curr_down_time, curr_up_time,
                                                          last_dSta, last_uSta, last_op_rate, last_packet_length)

                # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                if max(curr_down_time, curr_up_time) > 40 ** 5:
                    # print('time out!')
                    break

            # record the throughput
            throughput_t.append(traffic_amount * 8 / max(curr_down_time, curr_up_time))
            delay_t.append(max(curr_down_time,curr_up_time)-overhead_time/1000/count + overhead_time)
        throughput.append(throughput_t)
        delay.append(delay_t)
    # print(throughput, delay)
    return throughput,delay

def test_Janus_scheduler():
    # in this test program, the Janus exchange period will be discussed and test the throughput under different traffic.
    throughput = []
    for i in range(5):
        throughput_t = []
        for numStation in numOfstations_list:
            stations_pos = np.array(genToplogy.rnd_top_square(num_node=numStation))
            matSIR = genMatSIR(stations_pos)
            matSIR = makeAllFullDuplex(matSIR)
            traffic_amount = 0
            for j in range(200):
                if i == 0: # saturated traffic with the same packet length
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 1, True)
                elif i == 1: # only upstream, nothing to download
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 1, 0, True)
                elif i == 2: # only downstream, nothing to upload
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0, 1, True)
                elif i == 3: # typical asymmetric traffic
                    upstream, downstream = trafficHandler.genAsymmetricTraffic(len(matSIR), True)
                elif i == 4: # random traffic
                    upstream, downstream = trafficHandler.generateUDtraffic(len(matSIR), 0.5, 0.5, True)

                traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                # start the contention free period
                if j == 0:
                    [curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length] \
                        = Janus.Janus_sim_exchange_period(upstream, downstream,matSIR)
                    # print(curr_down_time, curr_up_time)
                else:
                    [curr_down_time, curr_up_time, last_dSta, last_uSta, last_op_rate, last_packet_length] \
                        = Janus.Janus_sim_exchange_period(upstream, downstream, matSIR,curr_down_time, curr_up_time,
                                                          last_dSta, last_uSta, last_op_rate, last_packet_length)

                # checkout whether the contention free period is over, period = 100ms, that is 10**5 us
                if max(curr_down_time, curr_up_time) > 10 ** 5:
                    # print('time out!')
                    break

            # record the throughput
            throughput_t.append(traffic_amount * 8 / max(curr_down_time, curr_up_time))
        throughput.append(throughput_t)
    # print(throughput, delay)
    return throughput

def test_Janus_scheduler_trafficType_50times():
    global ws_line
    flag = True
    for i in range(0, 49):
        throughput = test_Janus_scheduler()

        write2xls(throughput[0], ws_line, 1)
        write2xls(throughput[1], ws_line, 2)
        write2xls(throughput[2], ws_line, 3)
        write2xls(throughput[3], ws_line, 4)
        write2xls(throughput[4], ws_line, 5)
        # write2xls(throughput[5], ws_line, 6)
        ws_line += 1
        if flag:
            throughput_sum = np.array(throughput)
            flag = False
        else:
            throughput_sum += np.array(throughput)
        # delay_sum += np.array(delay)

    throughput_ave = throughput_sum / 50

    ws_line += 2
    write2xls(throughput_ave[0], ws_line, 1)
    write2xls(throughput_ave[1], ws_line, 2)
    write2xls(throughput_ave[2], ws_line, 3)
    write2xls(throughput_ave[3], ws_line, 4)
    write2xls(throughput_ave[4], ws_line, 5)
    # ws_line = 0
    # for i in range(5):
    #     write2xls(delay_ave[i], ws_line, 6)
    #     ws_line += 1

    print((throughput_sum / 50).tolist())

def test_Janus_trafficType_50times():
    global ws_line
    flag = True
    for i in range(0, 50):
        throughput, delay = test_Janus_trafficType()

        write2xls(throughput[0], ws_line, 1)
        write2xls(throughput[1], ws_line, 2)
        write2xls(throughput[2], ws_line, 3)
        write2xls(throughput[3], ws_line, 4)
        write2xls(throughput[4], ws_line, 5)
        # write2xls(throughput[5], ws_line, 6)
        ws_line += 1
        if flag:
            print(throughput[0])
            throughput_sum = np.array(throughput)
            delay_sum = np.array(delay)
            flag = False
        else:
            throughput_sum += np.array(throughput)
            delay_sum += np.array(delay)
    throughput_ave = throughput_sum / 50
    delay_ave = delay_sum/50

    ws_line += 2
    write2xls(throughput_ave[0], ws_line, 1)
    write2xls(throughput_ave[1], ws_line, 2)
    write2xls(throughput_ave[2], ws_line, 3)
    write2xls(throughput_ave[3], ws_line, 4)
    write2xls(throughput_ave[4], ws_line, 5)
    ws_line = 0
    for i in range(5):
        write2xls(delay_ave[i], ws_line, 6)
        ws_line += 1
    print((throughput_sum / 50).tolist())

# test_performance_with_saturated_traffic_50times()
# test_performance_betweend_different_protocols_different_packet_length()
# test_throughput_with_different_CFP()
# plotTop(top_rnd_10)
# test_deltaPower_50times()
# test_trafficType_50times()
# test_50times()
test_Janus_trafficType_50times()
########################################################################################################################
wb.save('tmp.xls')
########################################################################################################################
