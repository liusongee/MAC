import PCF
import trafficHandler
import numpy as np
import xlwt

numOfstations_list = np.arange(5, 105, 5)

def test_PCF_traffic():
    throughput = []
    delay = []
    for i in range(5):
        throughput_tmp = []
        delay_tmp = []
        for Station_num in numOfstations_list:
            traffic_amount = 0
            for j in range(100):
                # saturated traffic with different packet length
                if i == 0:  # saturated traffic with the same packet length
                    upstream, downstream = trafficHandler.generateUDtraffic(Station_num, 1, 1, True)
                elif i == 1:  # only upstream, nothing to download
                    upstream, downstream = trafficHandler.generateUDtraffic(Station_num, 1, 0, True)
                elif i == 2:  # only downstream, nothing to upload
                    upstream, downstream = trafficHandler.generateUDtraffic(Station_num, 0, 1, True)
                elif i == 3:  # typical asymmetric traffic
                    upstream, downstream = trafficHandler.genAsymmetricTraffic(Station_num, True)
                elif i == 4:  # random traffic
                    upstream, downstream = trafficHandler.generateUDtraffic(Station_num, 0.5, 0.5, True)
                traffic_amount += np.sum(np.array(upstream)) + np.sum(np.array(downstream))

                if not j:
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, current_time=0, need_ACK=False, Vt=18)
                else:
                    [PCF_timer, PCF_ACK] = PCF.PCF_sim(upstream, downstream, current_time=PCF_timer, need_ACK=PCF_ACK, Vt=18)

            throughput_tmp.append(traffic_amount*8/PCF_timer)
            delay_tmp.append(PCF_timer/100/1000)

        throughput.append(throughput_tmp.copy())
        delay.append(delay_tmp.copy())

    write2excel(throughput, delay)

def write2excel(throughput, delay):
    wb = xlwt.Workbook()
    ws1 = wb.add_sheet('throughput')
    ws2 = wb.add_sheet('delay')

    (line, col) = np.shape(throughput)

    for line_num in range(line):
        for col_num in range(col):
            ws1.write(line_num, col_num, float(throughput[line_num][col_num]))

    for line_num in range(line):
        for col_num in range(col):
            ws2.write(line_num, col_num, float(delay[line_num][col_num]))

    wb.save('tmp1.xls')

test_PCF_traffic()