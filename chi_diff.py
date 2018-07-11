from random import randrange as r
from math import log2
import sys
from kernel import getOneBitPos
import main


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
    rho_cons = [[0, 36, 3, 105, 210], [1, 300, 10, 45, 66], [190, 6, 171, 15, 253], [28, 55, 153, 21, 120], [91, 276, 231, 136, 78]]
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


if __name__ == "__main__":
    # define w
    w = 64
    print("For w = :", w)
    trail(w)
    trails = kernel_vortex(w)
    if len(trails) > 0:
        for x in trails:
            print("a0 : ", x)
            a1 = []
            for tup in x:
                t = applyrho( tup[0], tup[1], tup[2], w )
                a1.append( pi( t[0], t[1], t[2] ) )
            print("a1 : ", a1)
            print("====================================================================================")
