from chi_diff import *


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
            for (x2, y2) in points:
                for (x3, y3) in points:
                    for (x4, y4) in points:
                        for (x5, y5) in points:
                            # for (x6, y6) in points:
                            #     for (x7, y7) in points:
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
                                                # choose z0 freely
                                                z0 = r(0, 5)
                                                z2 = (z0 + rho(x1, y1, w) - rho(x2, y2, w)) % w
                                                z4 = (z2 + rho(x3, y3, w) - rho(x4, y4, w)) % w
                                                # verification step
                                                if z0 != ( (z4 + rho(x5, y5, w) - rho(x0, y0, w)) % w ):
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

def kernel_vortex(e, w):
    """
        Section 2.4.5 Pg 27.
    """
    
    # need to generate e no. of active points in a0
    if e == 6:
        return active6(w)
    elif e == 8:
        pass
    

if __name__ == "__main__":
    # define w
    w = 64
    # no. of points, will vary if result not found
    e = 6
    print("For w = :", w)
    trails = kernel_vortex(e, w)
    if len(trails) > 0:
        for x in trails:
            print("a0 : ", x)
            a1 = []
            for tup in x:
                t = applyrho( tup[0], tup[1], tup[2], w )
                a1.append( pi( t[0], t[1], t[2] ) )
            print("a1 : ", a1)
            print("====================================================================================")
