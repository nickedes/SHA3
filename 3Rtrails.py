from chi_diff import *
from main import round_iota, round_iotaChi
from kernel import satisfyCon, getOneBitPos


def createState(trail, w = 64):
    """
        Create a State from differential trail
    """
    A = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    for bit in trail:
        x,y,z = bit
        A[x][y][z] = 1
    return A


def allunique2(a0, a1, a2, a3, a4, a5, a6, a7):
    """
    """
    vortex = list((a0, a1, a2, a3, a4, a5, a6, a7))
    if len(vortex) == len( set(vortex) ):
        return True
    return False


def active6(w):
    """
        Section 2.4.5 Pg 27. Keccak Reference For details
    """
    points = []
    for x in range(5):
        for y in range(5):
            points.append((x, y))
    c = 0
    # character of the vortex
    Cv = -1
    trails = []
    for (x0, y0) in points:
        for (x1, y1) in points:
            if x0 != x1 :
                continue
            for (x2, y2) in points:
                for (x3, y3) in points:
                    if x2 != x3 :
                        continue
                    for (x4, y4) in points:
                        for (x5, y5) in points:
                            # from I, II and III
                            if x0 == x1 and x2 == x3 and x4 == x5\
                             and y1 == y2 and y3 == y4 and y5 == y0:
                                # z0 == z1 and z2 == z3 and z4 == z5
                                # from IV
                                # dv = rho(x0, y0, w) + rho(x2, y2, w) + rho(x4, y4, w) + rho(x6, y6, w) - (rho(x1, y1, w) + rho(x3, y3, w) + rho(x5, y5, w) + rho(x7, y7, w))
                                dv = rho(x0, y0, w) + rho(x2, y2, w) + rho(x4, y4, w) - (rho(x1, y1, w) + rho(x3, y3, w) + rho(x5, y5, w))
                                dv = abs(dv)
                                if dv % w == 0:
                                    if pi(x1 , y1)[0] == pi(x2, y2)[0] and pi(x3 , y3)[0] == pi(x4, y4)[0] and pi(x5, y5)[0] == pi(x0, y0)[0]:
                                        for z0 in range(0, 5):
                                            # choose z0 freely
                                            z2 = (z0 + rho(x1, y1, w) - rho(x2, y2, w)) % w
                                            z4 = (z2 + rho(x3, y3, w) - rho(x4, y4, w)) % w
                                            # verification step
                                            if z0 != (z4 + rho(x5, y5, w) - rho(x0, y0, w)) % w:
                                                continue
                                            if dv > 0:
                                                Cv = max(Cv, log2(dv))
                                            a00 = (x0, y0, z0)
                                            a01 = (x1, y1, z0)
                                            a02 = (x2, y2, z2)
                                            a03 = (x3, y3, z2)
                                            a04 = (x4, y4, z4)
                                            a05 = (x5, y5, z4)
                                            if not allunique(a00, a01, a02, a03, a04, a05):
                                                continue
                                            c += 1
                                            # print(a00, a01, a02, a03, a04, a05)
                                            trails.append( [a00, a01, a02, a03, a04, a05] )
    print("No. of trails = ", c, ", Character of Vortex : ", Cv)
    return trails


def active8(w):
    """
        Section 2.4.5 Pg 27. Keccak Reference For details
    """
    points = []
    for x in range(5):
        for y in range(5):
            points.append((x, y))
    c = 0
    # character of the vortex
    Cv = -1
    trails = []
    for (x0, y0) in points:
        for (x1, y1) in points:
            if x0 != x1:
                continue
            for (x2, y2) in points:
                for (x3, y3) in points:
                    if x2 != x3:
                        continue
                    for (x4, y4) in points:
                        for (x5, y5) in points:
                            if x4 != x5:
                                continue
                            for (x6, y6) in points:
                                for (x7, y7) in points:
                                    # from I, II and III
                                    if x0 == x1 and x2 == x3 and x4 == x5 and x6 == x7\
                                     and y1 == y2 and y3 == y4 and y5 == y6 and y7 == y0:
                                        # z0 == z1 and z2 == z3 and z4 == z5
                                        # from IV
                                        dv = rho(x0, y0, w) + rho(x2, y2, w) + rho(x4, y4, w) + rho(x6, y6, w) - (rho(x1, y1, w) + rho(x3, y3, w) + rho(x5, y5, w) + rho(x7, y7, w))
                                        # dv = rho(x0, y0, w) + rho(x2, y2, w) + rho(x4, y4, w) - (rho(x1, y1, w) + rho(x3, y3, w) + rho(x5, y5, w))
                                        dv = abs(dv)
                                        if dv % w == 0:
                                            if pi(x1 , y1)[0] == pi(x2, y2)[0] and pi(x3 , y3)[0] == pi(x4, y4)[0] and pi(x5, y5)[0] == pi(x6, y6)[0] and pi(x7, y7)[0] == pi(x0, y0)[0]:
                                                # choose z0 freely
                                                for z0 in range(0, 5):
                                                    z2 = (z0 + rho(x1, y1, w) - rho(x2, y2, w)) % w
                                                    z4 = (z2 + rho(x3, y3, w) - rho(x4, y4, w)) % w
                                                    z6 = (z4 + rho(x5, y5, w) - rho(x6, y6, w)) % w
                                                    # verification step
                                                    if z0 != (z6 + rho(x7, y7, w) - rho(x0, y0, w)) % w:
                                                        continue
                                                    if dv > 0:
                                                        Cv = max(Cv, log2(dv))
                                                    a00 = (x0, y0, z0)
                                                    a01 = (x1, y1, z0)
                                                    a02 = (x2, y2, z2)
                                                    a03 = (x3, y3, z2)
                                                    a04 = (x4, y4, z4)
                                                    a05 = (x5, y5, z4)
                                                    a06 = (x6, y6, z6)
                                                    a07 = (x7, y7, z6)
                                                    if not allunique2(a00, a01, a02, a03, a04, a05, a06, a07):
                                                        continue
                                                    c += 1
                                                    # print(a00, a01, a02, a03, a04, a05)
                                                    trails.append( [a00, a01, a02, a03, a04, a05, a06, a07] )
    print("No. of trails = ", c, ", Character of Vortex : ", Cv)
    return trails


def verify_trails(trails, w = 64):
    """
    """
    # differential path requirements
    # input diff cant have these lanes
    negative_init = [(3,2), (4,2), (0,3), (1,3), (2,3), (3,3), (4,3), (0,4) , (1,4), (2,4), (3,4), (4,4)]

    negative_out = [(0,0), (1,0), (2,0), (3,0), (4,0), (0,1)]
    i = 0
    for trail in trails:
        i+=1
        for tupl in trail:
            if tupl in negative_init:
                print("Neg : ",i)
                break
        a0 = createState(trail, w)
        print("a0 : ", trail)
        # 1st round
        a1 = round_iotaChi(a0, w)
        print("a1 : ", getOneBitPos(a1, w))

        # 2nd round
        a2 = round_iotaChi(a1, w)
        delta3 = getOneBitPos(a2, w)
        print("a2 : ", delta3)
        if satisfyCon(delta3, negative_out):
            print("found")
            input()
        else:
            print(i)


def kernel_vortex(e, w):
    """
        Section 2.4.5 Pg 27.
    """
    
    # need to generate e no. of active points in a0
    if e == 6:
        return active6(w)
    elif e == 8:
        return active8(w)

    

if __name__ == "__main__":
    # define w
    w = 64
    # no. of points, will vary if result not found
    e = 6
    print("For w = :", w)
    trails = kernel_vortex(e, w)
    verify_trails(trails, w)
    # if len(trails) > 0:
    #     for x in trails:
    #         print("a0 : ", x)
    #         a1 = []
    #         for tup in x:
    #             t = applyrho( tup[0], tup[1], tup[2], w )
    #             a1.append( pi( t[0], t[1], t[2] ) )
    #         print("a1 : ", a1)
    #         a1State = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    #         for bit in a1:
    #             x,y,z = bit
    #             a1State[x][y][z] = 1
    #         a2 = round_iota(a1State, w)
    #         print("====================================================================================")
