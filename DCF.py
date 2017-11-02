from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import numpy as np
########################################################################################################################
## this program is to evaluate the thoughput perormance of 802.11 DCF.
## 1) base mechanism without RTS/CTS
## 2) mechanism with RTS/CTS
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

numOfstations_list = np.arange(5, 55, 5)

n_list = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
L_payload_list = [64, 128, 256, 512, 1024, 2048, 4096, 6000, 8000, 10000]
########################################################################################################################
## solve the equation of probability for transmitting in the next slot(Pt) and probability for collision(Pc)
## the equation is deduced by morkov chains
########################################################################################################################
def f_intermediate(x):
    Pt = x[0]
    Pc = x[1]
    return [2*(2*Pc-1)/((2*Pc-1)*(CWmin+1) + Pc*CWmin*((2*Pc)**m - 1)) - Pt,
             1 - Pc - (1-Pt)**(n - 1)]

def getDCFThroughputBase(para_n, para_CWmin=32, para_m=3):
    global n, CWmin, m
    n = para_n
    CWmin = para_CWmin
    m = para_m

    result1 = fsolve(f_intermediate, [0.5, 0.1])
    # print(result1)
    Pt = result1[0]
    Pc = result1[1]
    ####################################################################################################################
    ## caculate the transmission time
    T_Send_base = (L_PHYhdr + L_MAChdr + L_payload) / V_t + T_SIFS + T_propagation + L_ACK / V_t + T_DIFS + T_propagation
    T_collide_base = (L_PHYhdr + L_MAChdr + L_payload) / V_t + T_DIFS + T_propagation

    T_send = T_Send_base
    T_collide = T_collide_base

    ## caculate the transmission probability
    P_tr = 1 - (1 - Pt) ** n
    P_s = n * Pt * (1 - Pt) ** (n - 1) / P_tr

    ## caculate the throughput
    return  P_s * P_tr * L_payload * 8 / ((1 - P_tr) * T_slot + P_tr * P_s * T_send + P_tr * (1 - P_s) * T_collide)

## using RTS/CTS mechanism

def getDCFThroughputRTS(para_n, para_CWmin=32, para_m=3):
    global n, CWmin, m
    n = para_n
    CWmin = para_CWmin
    m = para_m

    result1 = fsolve(f_intermediate, [0.5, 0.1])
    # print(result1)
    Pt = result1[0]
    Pc = result1[1]
    ####################################################################################################################
    ## caculate the transmission time
    T_Send_rts = L_RTS / V_t + T_SIFS + T_propagation + L_CRS / V_t + T_SIFS + T_propagation + \
                 (L_PHYhdr + L_MAChdr + L_payload) / V_t + T_SIFS + T_propagation + L_ACK / V_t + T_DIFS + T_propagation
    T_collide_rts = L_RTS / V_t + T_DIFS + T_propagation

    T_send = T_Send_rts
    T_collide = T_collide_rts

    ## caculate the transmission probability
    P_tr = 1 - (1 - Pt) ** n
    P_s = n * Pt * (1 - Pt) ** (n - 1) / P_tr

    ## caculate the throughput
    return P_s * P_tr * L_payload * 8 / ((1 - P_tr) * T_slot + P_tr * P_s * T_send + P_tr * (1 - P_s) * T_collide)



########################################################################################################################
throughput = []
throughput1 = []
for n in numOfstations_list:
    throughput.append(getDCFThroughputBase(n, 32, 3))
    throughput1.append(getDCFThroughputRTS(n, 32, 3))
print(throughput,throughput1)
# throughput = []
# throughput1 = []
# for n in L_payload_list:
#     L_payload = n
#     throughput.append(getDCFThroughputBase(50, 32, 3))
#     throughput1.append(getDCFThroughputRTS(50, 32, 3))
########################################################################################################################

if True:
    plt.figure(1,facecolor='w')
    plt.style.use('ggplot')

    plt.plot(numOfstations_list,throughput,'-o',lw=1,label='basic,W=32,m=3')
    plt.plot(numOfstations_list,throughput1,'-x',lw=1,label='RTS/CTS,W=32,m=3')

    plt.xlabel('Number of stations')
    plt.ylabel('Throughput')
    plt.legend(loc=0)

    plt.show()
