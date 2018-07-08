from random import randrange as r
from math import log2
import sys


def allunique(a0, a1, a2, a3, a4, a5):
    """
    """
    vortex = list((a0, a1, a2, a3, a4, a5))
    if len(vortex) == len( set(vortex) ):
        return True
    return False


def pi(x,y,z=0):
    """
        Apply Pi on lane at x,y
    """
    X = (0*x + 1*y) % 5
    Y = (2*x + 3*y) % 5
    return (X, Y, z)


def applyrho(x,y,z, w):
    """
        Apply rho mapping
    """
    rho_c = rho(x, y, w)
    Z = (z + rho_c) % w
    return (x, y, Z)


def chi(A):
    """
    Chi step mapping - XOR each bit with Non linear operation of two other bits in the same row
    Input A : row (5 bits)
    """
    A_ = [0 for x in range(5)]
    for x in range(5):
        A_[x] = A[x] ^ (
                    (A[(x+1) % 5] ^ 1) * A[(x+2) % 5])
    return A_


def chi_dff():
    """
        Gives the input-output pairs for Sbox Chi
    """
    for indiff in range(32):
        maps = {}
        # input diff
        bitlist = "{:05b}".format(indiff)
        a = [int(i) for i in bitlist]
        # output diffs
        # b
        # print("     a                 m1              m2              o1              o2              b")
        for x in range(32):
            bitlist = "{:05b}".format(x)
            m1 = [int(i) for i in bitlist]
            m2 = []
            for i in range(5):
                m2.append(m1[i] ^ a[i])
            o1 = chi(m1)
            o2 = chi(m2)
            b = []
            for i in range(5):
                b.append(o1[i] ^ o2[i])
            # print(a, m1, m2, o1, o2, b)
            val = ''.join(map(str, b))
            if val not in maps:
                maps[val] = 1
            else:
                maps[val] += 1
        print(maps)


def rho(x, y, w):
    """
        rho for lane position (x,y)
    """
    rho_cons = [[0, 36, 3, 105, 210], [1, 300, 10, 45, 66], [190, 6, 171, 253, 15], [28, 55, 153, 21, 120], [91, 276, 231, 136, 78]]
    return rho_cons[x][y] % w


def trail(w):
    points = []
    for x in range(5):
        for y in range(5):
            points.append((x, y))
    for (x0, y0) in points:
        for (x2, y2) in points:
            if x0 != x2 and y0 != y2:
                if (rho(x0, y0, w) - rho(x0, y2, w) + rho(x2, y2, w) - rho(x2, y0, w)) % w == 0:
                    # choose z0 freely
                    z0 = r(0, 5)
                    z2 = (z0 + rho(x0, y2, w) - rho(x2, y2, w)) % w
                    a00 = (x0, y0, z0)
                    a01 = (x0, y2, z0)
                    a02 = (x2, y2, z2)
                    a03 = (x2, y0, z2)
                    print(a00, a01, a02, a03)

def kernel_vortex(w):
    """
        Section 2.4.5 Pg 27.
    """
    # no. of points, will vary if result not found
    e2 = 4*4
    # need to generate e2 no. of points
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
    print("No. of trails, Character of Vortex : ",c, Cv)
    return trails


if __name__ == "__main__":
    # main()
    # define w
    # w = 16
    # print("For w = :", w)
    # trail(w)
    # w = 32
    # print("For w = :", w)
    # trail(w)
    w = 64
    print("For w = :", w)
    trail(w)
    trails = kernel_vortex(w)
    if len(trails) > 0:
        x = trails[0]
        print("a0 : ", x)
        a1 = []
        for tup in x:
            t = applyrho( tup[0], tup[1], tup[2], w )
            a1.append( pi( t[0], t[1], t[2] ) )
        print("a1 : ", a1)
