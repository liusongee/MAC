#-*-coding:utf-8 -*-

from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import numpy as np
import random
import DCF
########################################################################################################################
## this program is to evaluate the thoughput perormance of a directional MAC protocol.
# |---uplink----|----downlink----|
#   contention-free + contention（traditional CSMA）
########################################################################################################################

########################################################################################################################
##　Global parameter setting
########################################################################################################################
# bytes
L_payload = 1024
L_MAChdr = 14
L_PHYhdr = 16
L_ACK = 14 + L_PHYhdr
L_RTS = 20 + L_PHYhdr
L_CRS = 14 + L_PHYhdr

V_t = 18/8 #Mbps

T_propagation = 1
T_slot = 8
T_SIFS = 10
T_DIFS = 50

T_ACKtimout = 300
T_CTStimout = 300

CWmin = 32
m = 3

M = 16
Pd = 1
Pu = 0

numOfstations_list = np.arange(5, 210, 10)

########################################################################################################################
## solve the equation of probability for transmitting in the next slot(Pt) and probability for collision(Pc)
## the equation is deduced by morkov chains
########################################################################################################################
def getCMACThroughput(n, para_CWmin=32, para_m=3):
    T_down = (L_PHYhdr + L_MAChdr + L_payload) / V_t + T_SIFS + T_propagation + T_propagation + L_ACK / V_t + T_DIFS
    thoughput_down =(1-((M-1)/M)**n)*L_payload * 8/T_down #

    throughput_up = DCF.getDCFThroughputRTS(n, para_CWmin, para_m)
    # print(throughput_up, thoughput_down)
    return thoughput_down * Pd + throughput_up*Pu

def getBaseRTS(para_n, para_CWmin=32, para_m=3,times = 200):
    throughputRTS = 0
    for t in range(0,times):
        num_vector = np.zeros(M,dtype=int)
        for i in range(0,para_n):
            k = random.randint(0,M-1)
            num_vector[k] += 1

        tmp_throughput = 0
        for i in range(0, M):
            if num_vector[i] == 0:
                continue
            tmp_throughput += 1/M * DCF.getDCFThroughputRTS(num_vector[i] + 1, para_CWmin, para_m)
        throughputRTS += 1/times * tmp_throughput
    # print(num_vector,tmp_throughput,throughput)
    return throughputRTS

def getBase(para_n, para_CWmin=32, para_m=3,times = 200):
    throughputbase = 0
    for t in range(0,times):
        num_vector = np.zeros(M,dtype=int)
        for i in range(0,para_n):
            k = random.randint(0,M-1)
            num_vector[k] += 1

        tmp_throughput = 0
        for i in range(0, M):
            if num_vector[i] == 0:
                continue
            tmp_throughput += 1/M * DCF.getDCFThroughputBase(num_vector[i] + 1, para_CWmin, para_m)
        throughputbase += 1/times * tmp_throughput
    # print(num_vector,tmp_throughput,throughput)
    return throughputbase
########################################################################################################################
def test():
    throughput = []
    throughput1 = []
    throughput2 = []
    for n in numOfstations_list:
        throughput.append(getBase(n, 32, 3))
        throughput1.append(getBaseRTS(n, 32, 3))
        throughput2.append(getCMACThroughput(n, 32, 3))
    return [throughput,throughput1,throughput2]

########################################################################################################################

if True:
    throughput, throughput1, throughput2 = test()
    fz = 15
    mz = 10
    f1, ax1 = plt.subplots(1,1,facecolor='w')
    # plt.style.use('ggplot')

    plt.plot(numOfstations_list,throughput,'-o', markersize=mz,lw=1,label='basic,W=32,m=3')
    plt.plot(numOfstations_list,throughput1,'-x', markersize=mz,lw=1,label='RTS/CTS,W=32,m=3')
    plt.plot(numOfstations_list,throughput2,'-d', markersize=mz,lw=1,label='CMAC,W=32,m=3')

    plt.xlabel('Number of stations',size=fz)
    plt.ylabel('Throughput',size=fz)
    plt.legend(loc=0)
    # plt.xlim(0,50)
    for ax in [ax1]:
        leg = ax.legend(loc=0, fontsize=fz)
        leg.get_frame().set_alpha(0.1)
        ax.yaxis.grid(True, which='major')
        ax.xaxis.grid(False)

    for ax in [ax1]:
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(fz)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(fz)

    plt.show()
