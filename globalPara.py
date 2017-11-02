#define the global parameter for the Medium Access protocol

#######################################################################################################################
## global parameter setting
#######################################################################################################################

#the packet length setting(bytes)
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
