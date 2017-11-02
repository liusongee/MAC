import  matplotlib.pyplot as plt
import  numpy as np
import trafficHandler

########################################################################################################################
numOfstations_list = np.arange(5, 55, 5)
numOfstations_list1 = np.arange(10, 110, 20)
packetLength_list = np.array([64, 128, 256, 512, 1024])
########################################################################################################################
throughput_under_saturatedTraffic_with_different_networksize = np.array(
    [[27.993005155451883, 28.036663417714898, 27.87327017637049, 27.875256610529004, 27.943475912336652,
      27.764991813948146, 27.890468926994572, 27.935043633533223, 27.673708029969237, 27.72853888814166],
     [15.811131566029882, 15.815550925166136, 15.80746991992906, 15.792526031846544, 15.810722833689015,
      15.823225135579515, 15.803812555035943, 15.81636984194447, 15.815022752147092, 15.808572857732099],
     [12.923920931248956, 13.033750867035437, 13.016287059715854, 12.973251903206622, 12.922281590451449,
      12.868406387064796, 12.813426032827046, 12.758058944839538, 12.702599386532224, 12.647157799520155],
     [12.688853334165897, 12.253120542235594, 11.641755053313913, 11.138765343511396, 10.709639949951603,
      10.333000835615433, 9.9955190407504144, 9.6884371301140444, 9.4057115481639784, 9.1429970765320228],
     [15.6, 15.55,15.5,15.45,15.4,15.35,15.3,15.25,15.2,15.1],
     [28.773338216540324, 28.385861726903467, 28.19056376242159, 28.360582603183957, 28.12997884495645,
      28.263413652441553, 28.080539786679815, 28.048829623360103, 27.920035035635888, 27.917867000347087]]
)

delay_under_saturatedTraffic_with_different_networksize = np.array(
    [[1.5425383372678936, 3.081361846126852, 4.628721083610435, 6.125482901416128, 7.711702765974774, 9.370296558922565,
      10.771151580246924, 12.368576203703714, 14.040905158730174, 15.520168452380961],
     [2.7236169902674536, 5.4577511896456, 8.156742045297669, 10.805382367465462, 13.621720319088272, 16.4356132525252,
      19.000434765432033, 21.839034320987583, 24.55587460317452, 27.20722507936499],
     ]
)

throughput_traffictype = np.array([
    [16.023477427892534, 21.930649274819704, 26.815559704535787, 29.874825050759725, 31.580739638158835],
    [9.3456439992156515, 12.277250585043122, 14.563459664462899, 16.057987175912899, 16.926137928923492],
    [8.6398306542070209, 11.78417894258769, 14.217630328828747, 15.882686310272666, 16.830479677280181],
    [10.204443184636904, 15.209908486944268, 22.034156076600361, 27.055050212944899, 30.164237511347913],
    [10.576177236104664, 15.789276250167138, 21.495674593901335, 26.17478566805072, 29.987369393038417],
    [28.341651636687526, 28.420099438778493, 27.983308497431626, 28.291991519998902, 28.026656399537963]]
)
delay_traffictype = np.array([
    [0.63906227883935696, 0.93385288065842598, 1.5274713804713804, 2.742108108108126, 5.1879722222222124],
    [0.54784881602912594, 0.83406296296297622, 1.40625925925928, 2.5507555555555745, 4.8398518518518383],
    [0.59260420775804235, 0.86896168582377253, 1.440465079365103, 2.5789088319088522, 4.8673597883597779],
    [0.50174222222220932, 0.67324533929903063, 0.92946604938272048, 1.5139502487562218, 2.7157987987987879],
    [0.48340526033279235, 0.65317388167387902, 0.95547195767195836, 1.5292996632996667, 2.8879206349206261],
    [2.8796063492063522, 3.092101010101012, 3.0322491582491606, 3.1033602693602758, 3.156423611111113]]
)
throughput_traffictype_comparewithPCF = np.array([
    [[15.927290613762207, 21.90393792960241, 26.815145944373171, 30.066957864490313, 32.058753509850483],
     [8.3179590193154258, 11.37814536525986, 13.942958789306827, 15.714061880754496, 16.779779055318034]],
    [[9.3452297176144832, 12.279377148491086, 14.564482567888879, 16.057987175912899, 16.926137928923492],
     [5.4086449653137718, 8.3180398693087554, 11.378324062197773, 13.943249642568052, 15.714448107309416]],
    [[8.6185556057267494, 11.77573831692605, 14.223586256618297, 15.880931893069219, 16.830937074005426],
     [5.7889447236183083, 8.7604562737641807, 11.785166240409055, 14.244204018547027, 15.903364969801595]],
    [[10.170797688092339, 14.808691152041959, 22.062068185898582, 27.188623851999072, 30.115452636599198],
     [5.5922330097090551, 8.5333333333335766, 11.577889447236096, 14.091743119265923, 15.807890222984506]],
    [[10.493334782695609, 15.821721069558937, 21.611718464553412, 26.181614800133527, 28.230021755849638],
     [5.5476334567157259, 8.4102188753609894, 11.572068846130049, 14.135917862586512, 15.800202391361976]],
    [[27.559991562925237, 28.369484647814186, 28.352414205537681, 28.957909759963499, 27.795081886101602],
     [15.882399980255258, 15.8144182589725, 15.852261804200342, 15.873405308747669, 15.789416879028689]]]
)

delay_traffictype_comparewithPCF = np.array([
    [[0.64292165242166055, 0.93499169262719617, 1.5274949494949497, 2.7245855855856034, 5.1106166666666546],
     [1.2310712250711184, 1.7999418483903564, 2.9376835016835279, 5.2131651651652202, 9.7641333333333726]],
    [[0.54787310261078959, 0.83391851851853183, 1.4061604938271814, 2.5507555555555745, 4.8398518518518383],
     [0.94663266545227442, 1.2310592592592327, 1.7999135802469137, 2.9376222222222248, 5.2130370370370018]],
    [[0.59406706114397256, 0.86958454106281968, 1.4398619047619277, 2.5791937321937528, 4.8672275132275029],
     [0.88444444444441117, 1.1688888888888991, 1.7377777777778003, 2.8755555555555783, 5.1511111111110974]],
    [[0.50340201005023832, 0.69148582375478973, 0.92829012345679385, 1.5065124378109476, 2.720198198198188],
     [0.91555555555550372, 1.1999999999999658, 1.7688888888889018, 2.9066666666666938, 5.1822222222222409]],
    [[0.48159508547008056, 0.62941319444444044, 0.94674004192872141, 1.5892892416225799, 2.8935841269841189],
     [0.91093589743584547, 1.1840833333332907, 1.7681090146750651, 2.9435767195767464, 5.1699301587301711]],
    [[3.2429618055555589, 3.0394215686274504, 3.1022188552188559, 3.0716430976430997, 3.0622727272727297],
     [5.6273611111110915, 5.4524183006535782, 5.5484444444444243, 5.6036094276094062, 5.3907070707070508]]]
)
throughput_different_CFP = np.array([[26.728676661812358, 25.631448579773558, 24.318172368286287, 22.01920533641239, 21.64489115713294], [27.52043525472944, 27.133448778166944, 26.76497292837858, 25.872710958445236, 24.71798541235814], [28.167056713744234, 27.61353774647791, 27.508688268051923, 27.262893157113513, 26.821040679735013], [28.153729626417174, 28.231308813547496, 28.380129582623404, 28.15416508664243, 27.779228178096737], [28.07954425604283, 28.441914524273546, 28.490187840287184, 28.604273821742776, 28.533866636691943]]
)
########################################################################################################################
def calculate_delay(throughput):
    delay_list = []

    for node_num in numOfstations_list:
        tmpT = np.zeros(5)
        for i in range(50):
            upstream, downstream = trafficHandler.generateUDtraffic(node_num, 1, 1, True,Plength=1024)
            traffic_amount = np.sum(np.array(upstream)) + np.sum(np.array(downstream))

            for j in range(5):
                tmpT[j] += traffic_amount*8/throughput_under_saturatedTraffic_with_different_networksize[j][numOfstations_list.tolist().index(node_num)]
        delay_list.append((tmpT/50/1000).tolist())
    return delay_list
delay_under_saturatedTraffic_with_different_networksize = np.array(calculate_delay(throughput_under_saturatedTraffic_with_different_networksize)).transpose()
print(delay_under_saturatedTraffic_with_different_networksize)
########################################################################################################################
def plot_saturated_networksize():
    fz = 18
    mz = 10
    f_networksize_differentprotocols, (ax1,ax2) = plt.subplots(1, 2, facecolor='w')

    ax1.plot(numOfstations_list[1::2], throughput_under_saturatedTraffic_with_different_networksize[0][1::2], 's-', markersize=mz, label='BiAP')
    ax1.plot(numOfstations_list[1::2], throughput_under_saturatedTraffic_with_different_networksize[4][1::2], '*-', markersize=mz, label='A-Duplex')
    ax1.plot(numOfstations_list[1::2], throughput_under_saturatedTraffic_with_different_networksize[1][1::2], 'd-', markersize=mz, label='802.11 PCF')
    ax1.plot(numOfstations_list[1::2], throughput_under_saturatedTraffic_with_different_networksize[2][1::2], 'o-', markersize=mz, label='802.11 DCF RTS/CTS')
    ax1.plot(numOfstations_list[1::2], throughput_under_saturatedTraffic_with_different_networksize[3][1::2], 'x-', markersize=mz, label='802.11 DCF')
    ax1.plot(numOfstations_list[1::2], throughput_under_saturatedTraffic_with_different_networksize[5][1::2], 'D-', markersize=mz, label='BiAP+FDStations')

    ax1.set_title('(a) Throughput',size = fz)
    ax1.set_ylabel('Throughput (Mbps)', size=fz)
    ax1.set_xlabel('Number of Stations', size=fz)

    leg = ax1.legend(loc=(0.1,0.4), fontsize=fz)
    leg.get_frame().set_alpha(0.1)
    ax1.yaxis.grid(True, which='major')
    ax1.xaxis.grid(False)

    ax2.plot(numOfstations_list[1::2], delay_under_saturatedTraffic_with_different_networksize[0][1::2], 's-', markersize=mz, label='BiAP')
    ax2.plot(numOfstations_list[1::2], delay_under_saturatedTraffic_with_different_networksize[4][1::2], '*-', markersize=mz, label='A-Duplex')
    ax2.plot(numOfstations_list[1::2], delay_under_saturatedTraffic_with_different_networksize[1][1::2], 'd-', markersize=mz, label='802.11 PCF')
    ax2.plot(numOfstations_list[1::2], delay_under_saturatedTraffic_with_different_networksize[2][1::2], 'o-', markersize=mz, label='802.11 DCF RTS/CTS')
    ax2.plot(numOfstations_list[1::2], delay_under_saturatedTraffic_with_different_networksize[3][1::2], 'x-', markersize=mz, label='802.11 DCF')

    ax2.set_title('(b) Average Delay', size = fz)
    ax2.set_ylabel('Average Delay (ms)', size=fz)
    ax2.set_xlabel('Number of Stations', size=fz)

    leg = ax2.legend(loc=0, fontsize=fz)
    leg.get_frame().set_alpha(0.1)
    ax2.yaxis.grid(True, which='major')
    ax2.xaxis.grid(False)

    for ax in [ax1,ax2]:
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(fz)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(fz)
    plt.show()

def plot_different_packetlength():
    fz = 18
    mz = 10
    f_packetlength, (ax1, ax3) = plt.subplots(1, 2, facecolor='w')

    ax1.plot(range(len(packetLength_list)), throughput_traffictype[0], 's-', markersize=mz, label='TR1')
    ax1.plot(range(len(packetLength_list)), throughput_traffictype[1], 'd-', markersize=mz, label='TR2')
    ax1.plot(range(len(packetLength_list)), throughput_traffictype[2], '*-', markersize=mz, label='TR3')
    ax1.plot(range(len(packetLength_list)), throughput_traffictype[3], 'x-', markersize=mz, label='TR4')
    ax1.plot(range(len(packetLength_list)), throughput_traffictype[4], 'o-', markersize=mz, label='TR5')

    ax1.set_title('(a)',size=fz)
    ax1.set_ylabel('Throughput (Mbps)', size=fz)
    ax1.set_xlabel('Payload Length (Bytes)', size=fz)

    leg = ax1.legend(loc=0, fontsize=fz)
    leg.get_frame().set_alpha(0.1)
    ax1.yaxis.grid(True, which='major')
    ax1.xaxis.grid(False)
    leg = ax1.legend(loc=0, fontsize=fz)
    leg.get_frame().set_alpha(0.1)

    ax3.plot(range(len(packetLength_list)), delay_traffictype[0], 's-', markersize=mz, label='TR1')
    ax3.plot(range(len(packetLength_list)), delay_traffictype[1], 'd-', markersize=mz, label='TR2')
    ax3.plot(range(len(packetLength_list)), delay_traffictype[2], '*-', markersize=mz, label='TR3')
    ax3.plot(range(len(packetLength_list)), delay_traffictype[3], 'x-', markersize=mz, label='TR4')
    ax3.plot(range(len(packetLength_list)), delay_traffictype[4], 'o-', markersize=mz, label='TR5')

    ax3.set_title('(b)',size=fz)
    ax3.set_ylabel('Delay (ms)', size=fz)
    ax3.set_xlabel('Payload Length (Bytes)', size=fz)

    leg = ax3.legend(loc=0, fontsize=fz)
    leg.get_frame().set_alpha(0.1)
    ax3.yaxis.grid(True, which='major')
    ax3.xaxis.grid(False)

    plt.setp((ax1,ax3), xticks=range(len(packetLength_list)), xticklabels=['64', '128', '256', '512', '1024'])

    for ax in [ax1,ax3]:
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(fz)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(fz)

    plt.show()

def plot_different_packetlength_compareWithPCF():
    fz = 18
    mz = 10
    f_packetlength, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharey='row', sharex='col', facecolor='w')

    ax1.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[0][0], 's-', markersize=mz, label='BiAP TR1')
    ax1.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[1][0], 'd-', markersize=mz, label='BiAP TR2/3')
    # ax1.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[2][0], '*-', markersize=mz, label='BiAP TR3')
    ax1.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[0][1], 's--', markersize=mz, label='PCF TR1')
    ax1.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[1][1], 'd--', markersize=mz, label='PCF TR2/3')
    # ax1.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[2][1], '*--', markersize=mz, label='PCF TR3')

    ax2.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[3][0], 'x-', markersize=mz, label='BiAP TR4')
    ax2.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[4][0], 'o-', markersize=mz, label='BiAP TR5')
    ax2.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[3][1], 'x--', markersize=mz, label='PCF TR4')
    ax2.plot(range(len(packetLength_list)), throughput_traffictype_comparewithPCF[4][1], 'o--', markersize=mz, label='PCF TR5')

    ax3.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[0][0], 's-', markersize=mz, label='BiAP TR1')
    ax3.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[1][0], 'd-', markersize=mz, label='BiAP TR2/3')
    # ax3.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[2][0], '*-', markersize=mz, label='BiAP TR3')
    ax3.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[0][1], 's--', markersize=mz, label='PCF TR1')
    ax3.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[1][1], 'd--', markersize=mz, label='PCF TR2/3')
    # ax3.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[2][1], '*--', markersize=mz, label='PCF TR3')

    ax4.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[3][0], 'x-', markersize=mz, label='BiAP TR4')
    ax4.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[4][0], 'o-', markersize=mz, label='BiAP TR5')
    ax4.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[3][1], 'x--', markersize=mz, label='PCF TR4')
    ax4.plot(range(len(packetLength_list)), delay_traffictype_comparewithPCF[4][1], 'o--', markersize=mz, label='PCF TR5')


    ax1.set_title('(a)',size=fz)
    ax2.set_title('(b)', size=fz)
    ax3.set_title('(c)',size=fz)
    ax4.set_title('(d)',size=fz)

    ax1.set_ylabel('Throughput (Mbps)', size=fz)
    ax3.set_ylabel('Delay (ms)', size=fz)
    ax3.set_xlabel('Payload Length (Bytes)', size=fz)
    ax4.set_xlabel('Payload Length (Bytes)', size=fz)

    for ax in [ax1, ax2, ax3, ax4]:
        leg = ax.legend(loc=0, fontsize=fz)
        leg.get_frame().set_alpha(0.1)
        ax.yaxis.grid(True, which='major')
        ax.xaxis.grid(False)

    plt.setp((ax4,ax3), xticks=range(len(packetLength_list)), xticklabels=['64', '128', '256', '512', '1024'])

    for ax in [ax1, ax2, ax3, ax4]:
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(fz)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(fz)
    plt.show()

def plot_CFP():
    fz = 18
    mz = 10
    f_CFP, ax1 = plt.subplots(1, 1, facecolor='w')

    ax1.plot(numOfstations_list1, throughput_different_CFP[0], 's-', markersize=mz, label='$T_{CFP}$=20ms')
    ax1.plot(numOfstations_list1, throughput_different_CFP[1], 'd-', markersize=mz, label='$T_{CFP}$=50ms')
    ax1.plot(numOfstations_list1, throughput_different_CFP[2], 'o-', markersize=mz, label='$T_{CFP}$=100ms')
    ax1.plot(numOfstations_list1, throughput_different_CFP[3], '+-', markersize=mz, label='$T_{CFP}$=200ms')
    ax1.plot(numOfstations_list1, throughput_different_CFP[4], '*-', markersize=mz, label='$T_{CFP}$=400ms')
    ax1.set_ylabel('Throughput (Mbps)', size=fz)
    ax1.set_xlabel('Number of Stations', size=fz)

    leg = ax1.legend(loc=0, fontsize=fz)
    leg.get_frame().set_alpha(0.1)
    ax1.yaxis.grid(True, which='major')
    ax1.xaxis.grid(False)
    plt.setp((ax1), xticks=numOfstations_list1)
    for ax in [ax1]:
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(fz)
    for tick in ax1.yaxis.get_major_ticks():
        tick.label.set_fontsize(fz)

    plt.show()

########################################################################################################################
# plot_saturated_networksize()
# plot_different_packetlength()
# plot_different_packetlength_compareWithPCF()
plot_CFP()