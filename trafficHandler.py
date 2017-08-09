import random
########################################################################################################################
# Generate traffic vector: upstream & downstream
# flag: according with the traffic distribution on the Internet
########################################################################################################################
# node_num： the number of stations in the network
# up_probility/down_probility: the probility of packets to be sent on uplink/downlink channel.
# flag: means that whether the traffic distribution is in line with the actual traffic distribution
# Plength: default packet length
def generateUDtraffic(node_num, up_probility, down_probility, flag=False, Plength=1024):
    upstream = []
    downstream = []
    for i in range(node_num):
        rnd_size = random.randint(0, 99)
        if random.randint(0, 99) < up_probility * 100:
            if flag:
                if rnd_size < 40:
                    upstream.append(64)
                elif rnd_size < 60:
                    upstream.append(512)
                else:
                    upstream.append(1024)
            else:
                upstream.append(Plength)
        else:
            upstream.append(0)

        rnd_size = random.randint(0, 99)
        if random.randint(0, 99) < down_probility * 100:
            if flag:
                if rnd_size < 40:
                    downstream.append(64)
                elif rnd_size < 60:
                    downstream.append(512)
                else:
                    downstream.append(1024)
            else:
                downstream.append(Plength)
        else:
            downstream.append(0)
    return upstream, downstream

# generate the traffic in which some nodes only have upstream traffic and some only have downstream traffic
def genAsymmetricTraffic(num_node, distribution_flag, Plength = 1024):
    upstream = []
    downstream = []
    if distribution_flag:
        for i in range(num_node):
            if i % 2 == 0:
                upstream.append(packetLengthDistribution())
                downstream.append(0)
            else:
                upstream.append(0)
                downstream.append(packetLengthDistribution())
    else:
        for i in range(num_node):
            if i % 2 == 0:
                upstream.append(Plength)
                downstream.append(0)
            else:
                upstream.append(0)
                downstream.append(Plength)
    return upstream, downstream

# packet length distribution function
# small: the probility of small Payload length (64 bytes)
# medium: the probility of medium payload length (512 bytes)
# large: the probility of large payloadlength (1024 bytes)
def packetLengthDistribution(small=0.4, medium=0.2, large=0.4):
    rnd_size = random.randint(0, 99)
    if rnd_size < small * 100:
        return 64
    elif rnd_size < (small + medium) * 100:
        return 512
    elif rnd_size < (small + medium + large) * 100:
        return 1024
    else:
        print("error!!!!!!!!!!!!!!!!!!!!!")
        return 0
