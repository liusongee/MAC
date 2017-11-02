import numpy as np

# Vdirection is a unit vector, means the direction of the multi-beam directional antena
# center denotes the possition of transmitting node
# angle denotes the angle of multi-beam directional antenna
# pos denotes the possition of receiving node
def inSector(Vdirection, angle, center, pos):
    Vpos = pos - center
    Acos_pos = np.dot(Vdirection, Vpos)/(np.sqrt(Vdirection.dot(Vdirection))*np.sqrt(Vpos.dot(Vpos)))
    Apos = np.arccos(Acos_pos)
    # print(round(Apos,4), round(angle/2,4))
    if round(Apos,4) > round(angle/2,4):
        return False
    else:
        return True

def JFI_calculate(TestVector):
    a = TestVector.sum()
    b = len(TestVector)*(TestVector**2).sum()

    return a**2/b

def test_itself():
    Vdirection = np.array([1,0])
    angle = np.pi/2
    center = np.array([0,0])
    pos1 = np.array([1,1])
    pos2 = np.array([1,8])

    print(inSector(Vdirection, angle, center, pos1))
    print(inSector(Vdirection, angle, center, pos2))

    jfi = JFI_calculate(np.array([1,1,0,1,1,1,1,1]))

    print(jfi)

test_itself()
