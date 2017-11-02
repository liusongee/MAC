import  numpy as np
packet_length_list = [64,128,256,512,1024, 1500]

#######################################################################################################################
# simulate mechanism of 802.11 PCF
#######################################################################################################################

## global parameter setting
#######################################################################################################################

#the packet length setting
p_PHYhdr = 16
p_CFPoll_header = 16 + p_PHYhdr
p_FCS = 4
ACK = 14
p_Data = 2048

# Frame space setting (us)
T_SLOT = 8#20
T_SIFS = 10
T_PIFS = T_SIFS + T_SLOT
T_DIFS = T_SIFS + 2*T_SLOT
T_EIFS = T_SIFS + T_DIFS +T_SLOT

Vt = 18 #Mbps transmission rate
#######################################################################################################################
# compare with PCF
#######################################################################################################################
# upstream downstrem is the vector of packets to be tranffred in the network (of all staions)

def PCF_sim(upstream, downstrem, current_time = 0, need_ACK=False, Vt = 18):
    for i in range(len(upstream)):
        current_time += T_PIFS + (p_CFPoll_header + downstrem[i] + p_FCS)*8/Vt
        if need_ACK:
            current_time += ACK*8/Vt

        current_time += T_SIFS + (p_CFPoll_header + upstream[i] + p_FCS)*8/Vt
        if upstream[i] > 0:
            need_ACK = True
        else:
            need_ACK = False
    return  [current_time, need_ACK]
########################################################################################################################

