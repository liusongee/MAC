import random
import numpy as np
import matplotlib.pyplot as plt
import math
import tools
## generate a toplogy with num_node stations in a scope with scope[0] * scope[1]
# input:
#       num_node: the number of Stations
#       scope: the area staions deployment scope[0] * scope[1]
# output:
#       stations_pos(type: list): the possition of each station in the network
def rnd_top_square(num_node = 10, scope = [300, 300]):
    stations_pos = []
    for i in np.arange(0, num_node):
        stations_pos.append([random.randint(0, scope[0]), random.randint(0, scope[1])])

    return stations_pos

def rnd_top_cycle(num_node = 10, ratio_radius = 150):
    stations_pos = []
    for i in range(num_node):
        r = random.uniform(2, ratio_radius)
        angle = random.uniform(0, 2 * math.pi)

        stations_pos.append([r * math.cos(angle), r * math.sin(angle)])
        # print(topopogy_cycle)
    return stations_pos

def plot_rnd_top(stations_pos, AP_pos, scope):
    plt.style.use('seaborn-muted')
    plt.rc('grid', linestyle=":")

    plt.scatter(stations_pos[:, 0], stations_pos[:, 1], s=20, label='station')
    plt.scatter(AP_pos[0], AP_pos[1], s=80, label='AP')
    plt.text(AP_pos[0], AP_pos[1], 'AP')

    plt.xticks(np.arange(0, scope[0] + 30, 30))
    plt.yticks(np.arange(0, scope[1] + 30, 30))

    plt.legend(loc=0)
    plt.grid(True)
    plt.show()

################################################################################
# get the signal-to-interference ratio for the network
################################################################################
# pass loss function
def PathLoss(d,n=4):
    if d == 0:
        return 0
    return 48 + 10 * n * math.log10(d)


def signalAP2node(pos_nodes, pos_AP, signalPower):
    num = len(pos_nodes)
    signal_s = []
    for i in np.arange(0, num):
        signal_s.append(
            signalPower - PathLoss(math.sqrt((pos_nodes[i][0] - pos_AP[0]) ** 2 + (pos_nodes[i][1] - pos_AP[1]) ** 2)))

    return signal_s


# mat_interference[i][j] means the value of node i interferes node j.
# when the signal power of each node is the same, mat_interference[i][j] also means the value of node j interferes node i.
def interference(pos_nodes, signalPower):
    mat_interference = []
    num = len(pos_nodes)
    for i in np.arange(0, num):
        tmp = []
        for j in np.arange(0, num):
            signal_loss = PathLoss(
                math.sqrt((pos_nodes[i][0] - pos_nodes[j][0]) ** 2 + (pos_nodes[i][1] - pos_nodes[j][1]) ** 2))
            tmp.append(signalPower - signal_loss)
        mat_interference.append(tmp.copy())
    return mat_interference

def interference_with_directinalAntenna(pos_nodes, pos_AP, signalPower, angle):
    mat_interference = []
    num = len(pos_nodes)
    for i in np.arange(0, num):
        tmp = []
        for j in np.arange(0, num):
            # if node j in the coverage area of node i
            if np.array_equal(np.array(pos_AP), np.array(pos_nodes[i])):
                pos_nodes[i][0] -= 1
                pos_nodes[i][1] -= 1
            Vd = np.array(pos_AP) - np.array(pos_nodes[i])
            Vdirection = Vd/math.sqrt((Vd[0]) ** 2 + (Vd[1]) ** 2)
            if tools.inSector(Vdirection, angle, pos_nodes[i], pos_nodes[j]):
                signal_loss = PathLoss(
                    math.sqrt((pos_nodes[i][0] - pos_nodes[j][0]) ** 2 + (pos_nodes[i][1] - pos_nodes[j][1]) ** 2))
                tmp.append(signalPower - signal_loss)
            else:
                tmp.append(-80)
        mat_interference.append(tmp.copy())
    return mat_interference

# mat_SIR[i][j] means that node j's SIR with interference from node i.
def calc_SIR(pos_nodes, pos_AP, deltaPower = 10, signalPower = 100):
    mat_SIR = []
    num = len(pos_nodes)
    mat_interference = interference(pos_nodes, signalPower - deltaPower)
    v_signal_nodes = signalAP2node(pos_nodes, pos_AP, signalPower)

    for i in np.arange(0, num):
        tmp = []
        for j in np.arange(0, num):
            tmp.append(v_signal_nodes[j] - mat_interference[i][j])
        mat_SIR.append(tmp.copy())

    return mat_SIR

def calc_SIR_directional(pos_nodes, pos_AP, deltaPower = 10, signalPower = 100, angle=np.pi/6):
    mat_SIR = []
    num = len(pos_nodes)
    mat_interference = interference_with_directinalAntenna(pos_nodes, pos_AP, signalPower - deltaPower, angle)
    v_signal_nodes = signalAP2node(pos_nodes, pos_AP, signalPower)

    for i in np.arange(0, num):
        tmp = []
        for j in np.arange(0, num):
            tmp.append(v_signal_nodes[j] - mat_interference[i][j])
        mat_SIR.append(tmp.copy())

    return mat_SIR

def test_itself():
    AP_pos = [150, 150]
    stations_pos = np.array(rnd_top_square(20))
    plot_rnd_top(stations_pos, AP_pos, [300, 300])

# test_itself()
