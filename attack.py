from main import *
import itertools


def getreversePrintformat(digest):
    """
        Input is hex digest
        For example : 1a cc 22 0b 9e 2e a7 20 8d 48 61 ba b4 30 ae 45 b0 fc 48 10 62 1f 19 20 (or) 1acc220b9e2ea7208d4861bab430ae45b0fc4810621f1920
        Return Binary digest
    """
    out = ""
    for i in range(len(digest)//2):
        out += "{:08b}".format( int( digest[i*2 : (i+1)*2], 16) )[::-1]
    return out


def digestToState(bdigest, w):
    """
        From digest(binary) construct the state, with rest of lanes being 0 except the lanes with digest
    """
    filledlanes = len(bdigest) // w

    totalLanes = 25
    bdigest += '0'*((totalLanes - filledlanes)*w)
    A = getState(bdigest, w)
    return A


def iotainverse(A, i, w):
    """
        Same as iota, send the correct round index i
    """
    A_ = [[[A[x][y][z] for z in range(w)] for y in range(5)] for x in range(5)]

    RCi = {
        0: "0000000000000001", 12: "000000008000808B", 1: "0000000000008082", 13: "800000000000008B",
        2: "800000000000808A", 14: "8000000000008089", 3: "8000000080008000", 15: "8000000000008003",
        4: "000000000000808B", 16: "8000000000008002", 5: "0000000080000001", 17: "8000000000000080",
        6: "8000000080008081", 18: "000000000000800A", 7: "8000000000008009", 19: "800000008000000A",
        8: "000000000000008A", 20: "8000000080008081", 9: "0000000000000088", 21: "8000000000008080",
        10: "0000000080008009", 22: "0000000080000001", 11: "000000008000000A", 23: "8000000080008008"
    }

    # 64 bit repr for rc
    RC_bin = "{:032b}".format(int(RCi[i], 16))
    RC = [int(x) for x in RC_bin][::-1]
    for z in range(w):
        A_[0][0][z] = A_[0][0][z] ^ RC[z]

    # print("After iota")
    # printformat(getString(A_, w))
    # input()
    return A_


def ChiInverseForROW(row):
    """
        Row dependent operation
        Input : A row of state
    """
    rowinv = [0, 0, 0, 0, 0]
    for i in range(len(row)):
        rowinv[i] = row[i] ^ ((row[ (i + 1) % 5 ] ^ 1) * ( row[ (i + 2) % 5 ] ^ (( row[ (i + 3) % 5 ] ^ 1 ) * row[ (i + 4) % 5 ]) ) )
    return rowinv


def ChiInverse(A, w):
    # Step 1 :
    # lanes are fixed, we need to invert each row of the 1st 5 lanes
    for i in range(w):
        row = [ A[0][0][i], A[1][0][i], A[2][0][i], A[3][0][i], A[4][0][i] ]
        rowinv = ChiInverseForROW(row)
        A[0][0][i], A[1][0][i], A[2][0][i], A[3][0][i], A[4][0][i] = rowinv
    # Step 2 :
    # A[0][1] remains same and A[1][1] becomes 1

    for i in range(w):
        A[1][1][i] = 1
    return A


def rhoInverse(A, w):
    """
    rho step mapping - Rotate the bits of each lane by an offset.
    """
    # init for A_ ?

    A_ = [[[A[x][y][z] for z in range(w)] for y in range(5)] for x in range(5)]
    for z in range(w):
        A_[0][0][z] = A[0][0][z]
    x, y = 1, 0
    for t in range(24):
        for z in range(w):
            A_[x][y][z] = A[x][y][(z + ((t+1)*(t+2))//2) % w]
        x, y = y, (2*x + 3*y) % 5

    # print("After rho")
    # printformat(getString(A_, w))
    # input()
    return A_


def piInverse(A, w):
    """
    pi step mapping - Rearrange the positions of the lanes
    """
    A_ = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    for x in range(5):
        for y in range(5):
            for z in range(w):
                A_[x][y][z] = A[y % 5][(2*x + 3*y) % 5][z]
    # print("After pi")
    # printformat(getString(A_, w))
    # input()
    return A_


def applyChi(slicei):
    """
    Apply row operation on a slice
    """
    A = slicei
    A_ = [[0 for y in range(5)] for x in range(5)]
    for x in range(5):
        for y in range(5):
            A_[x][y] = A[x][y] ^ ((A[(x+1) % 5][y] ^ 1) * A[(x+2) % 5][y])
    return A_


def applytheta(slice1, slice2):
    """
        Apply theta for 2 slices
    """
    C = [[0 for z in range(2)] for x in range(5)]
    for x in range(5):
        for z in range(2):
            if z == 0:
                A = slice1
            else:
                A = slice2
            C[x][z] = A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4]

    D = [[0 for z in range(2)] for x in range(5)]

    for x in range(5):
        z = 1
        D[x][z] = C[(x-1) % 5][z] ^ C[(x+1) % 5][(z-1) % 2]

    A_ = [[0 for y in range(5)] for x in range(5)]

    for x in range(5):
        for y in range(5):
            z = 1
            A = slice1
            A_[x][y] = A[x][y] ^ D[x][z]

    return A_

def check( slice0, slice1, A, i):
    """
    """
    slice0 = applyChi(slice0)
    slice1 = applyChi(slice1)

    slicei = applytheta(slice0, slice1)

    if slicei[0][0] == A[0][0][i] and slicei[1][1] == A[1][1][i] and slicei[2][2] == A[2][2][i] and slicei[3][3] == A[3][3][i] and slicei[4][4] == A[4][4][i] and slicei[3][0] == A[3][0][i] and slicei[4][1] == A[4][1][i]:
        return True
    return False


def slices3(A, i):
    """
    """
    values = []
    for a00, a01, a10, a11, a20, a21, b00, b01, b10, b11, b20, b21 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
        for c00, c01, c10, c11, c20, c21, e00, e01, e10, e11 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
            # Check these 22 variables first
            slice0 = [ [a00, b20, c20, 0, 0], [0, e10, a10, 0, 0], [b00, c10, 0, 0, 0], [e00, a20, b10, 0, 0], [c00, 0, 0, 0, 0]]
            slice1 = [ [a01, b21, c21, 0, 0], [0, e11, a11, 0, 0], [b01, c11, 0, 0, 0], [e01, a21, b11, 0, 0], [c01, 0, 0, 0, 0]]

            result = check( slice0, slice1, A, i + 1)

            if result:
                for a02,a12,a22,b02,b12,b22,c02,c12,c22,e02,e12 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
                    slice1 = [ [a01, b21, c21, 0, 0], [0, e11, a11, 0, 0], [b01, c11, 0, 0, 0], [e01, a21, b11, 0, 0], [c01, 0, 0, 0, 0]]
                    slice2 = [ [a02, b22, c22, 0, 0], [0, e12, a12, 0, 0], [b02, c12, 0, 0, 0], [e02, a22, b12, 0, 0], [c02, 0, 0, 0, 0]]

                    result2 = check( slice1, slice2, A, i + 2)
                    if result2:
                        values.append([a00, a01, a02, a10, a11, a12, a20, a21, a22, b00, b01, b02, b10, b11, b12, b20, b21, b22, c00, c01, c02, c10, c11, c12, c20, c21, c22, e00, e01, e02, e10, e11, e12])
    return values


def phi3_0(a1_4, a2_4, a1_5, a2_5):
    """
    """
    x = (a1_4 + a2_4) % 2
    y = (a1_5 + a2_5) % 2
    return 2*x + y


def phi3_1(a0_3 , a0_5):
    """
    """
    return 2*a0_3 + a0_5


def merge3slices(A, i, slice3_0, slice3_1):
    """
    """
    values = []
    for slice3_0i in slice3_0:
        for slice3_1i in slice3_1:
            [a0_0, a0_1, a0_2, a1_3, a1_4, a1_5, a2_4, a2_5, a2_6, b0_1, b0_2, b0_3, b1_10, b1_11, b1_12, b2_12, b2_13, b2_14, c0_30, c0_31, c0_0, c1_6, c1_7, c1_8, c2_11, c2_12, c2_13, e0_27, e0_28, e0_29, e1_20, e1_21, e1_22] = slice3_0i
            [a0_3, a0_4, a0_5, a1_6, a1_7, a1_8, a2_7, a2_8, a2_9, b0_4, b0_5, b0_6, b1_13, b1_14, b1_15, b2_15, b2_16, b2_17, c0_1, c0_2, c0_3, c1_9, c1_10, c1_11, c2_14, c2_15, c2_16, e0_30, e0_31, e0_0, e1_23, e1_24, e1_25] = slice3_1i

            if phi3_0(a1_4, a2_4, a1_5, a2_5) == phi3_1(a0_4, a0_5):
                slice2 = [ [a0_2, b2_14, c2_13, 0, 0], [0, e1_22, a1_5, 0, 0], [b0_3, c1_8, 0, 0, 0], [e0_29, a2_6, b1_12, 0, 0], [c0_0, 0, 0, 0, 0]]
                slice3 = [ [a0_3, b2_15, c2_14, 0, 0], [0, e1_23, a1_6, 0, 0], [b0_4, c1_9, 0, 0, 0], [e0_30, a2_7, b1_13, 0, 0], [c0_1, 0, 0, 0, 0]]

                result = check( slice2, slice3, A, i + 3)
                # if output slice bits satisfied
                if result:
                    values.append([a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b2_12, b2_13, b2_14, b2_15, b2_16, b2_17, c0_30, c0_31, c0_0, c0_1, c0_2, c0_3, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c2_11, c2_12, c2_13, c2_14, c2_15, c2_16, e0_27, e0_28, e0_29, e0_30, e0_31, e0_0, e1_20, e1_21, e1_22, e1_23, e1_24, e1_25])
    return values


def phi6_0(a1_6, a2_6, a1_7, a2_7, a1_8, a2_8, a2_9, b1_12, b2_12, e0_27, e0_28, e0_29, e0_30, e0_31):
    """
    """
    return ((a1_6 + a2_6)%2) + 2*((a2_7 + a1_7)%2) + 4*((a2_8 + a1_8)%2) + 8*(a2_9) + 16*((b1_12 + b2_12) % 2) + 32*e0_27 + 64*e0_28 + 128*e0_29 + 256*e0_30 + 512*e0_31


def phi6_1(a0_6, a0_7, a0_8, a0_9, a1_9, b0_12, e1_27, e1_28, e1_29, e1_30, e1_31):
    """
    """
    return a0_6 + 2*a0_7 + 4*a0_8 + 8*( (a0_9 + a1_9) % 2) + 16*b0_12 + 32*e1_27, 64*e1_28 + 128*e1_29 + 256*e1_30 + 512*e1_31


def merge6slices(A, i, slice6_0, slice6_1):
    """
    """
    values = []
    for slice6_0i in slice6_0:
        for slice6_1i in slice6_1:
            [a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b2_12, b2_13, b2_14, b2_15, b2_16, b2_17, c0_30, c0_31, c0_0, c0_1, c0_2, c0_3, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c2_11, c2_12, c2_13, c2_14, c2_15, c2_16, e0_27, e0_28, e0_29, e0_30, e0_31, e0_0, e1_20, e1_21, e1_22, e1_23, e1_24, e1_25] = slice6_0i
            [a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b1_16, b1_17, b1_18, b1_19, b1_20, b1_21, b2_18, b2_19, b2_20, b2_21, b2_22, b2_23, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c1_12, c1_13, c1_14, c1_15, c1_16, c1_17, c2_17, c2_18, c2_19, c2_20, c2_21, c2_22, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e1_26, e1_27, e1_28, e1_29, e1_30, e1_31] = slice6_1i

            if phi6_0(a1_6, a2_6, a1_7, a2_7, a1_8, a2_8, a2_9, b1_12, b2_12, e0_27, e0_28, e0_29, e0_30, e0_31) == phi6_1(a0_6, a0_7, a0_8, a0_9, a1_9, b0_12, e1_27, e1_28, e1_29, e1_30, e1_31):
                slice5 = [ [a0_5, b2_17, c2_16, 0, 0], [0, e1_25, a1_8, 0, 0], [b0_6, c1_11, 0, 0, 0], [e0_0, a2_9, b1_15, 0, 0], [c0_3, 0, 0, 0, 0]]
                slice6 = [ [a0_6, b2_18, c2_17, 0, 0], [0, e1_24, a1_9, 0, 0], [b0_7, c1_12, 0, 0, 0], [e0_1, a2_10, b1_16, 0, 0], [c0_4, 0, 0, 0, 0]]

                result = check( slice5, slice6, A, i + 6)
                # if output slice bits satisfied
                if result:
                    values.append()
    return values


if __name__ == '__main__':
    # size of state
    state_size = 800

    w = state_size//25

    digest = "1acc220b9e2ea7208d4861bab430ae45b0fc4810621f1920"

    bdigest = getreversePrintformat(digest)

    # Got State 4, Fig 9
    A = digestToState(bdigest, w)

    # Step 1 : Iota inverse (we initially has 2 rounds, so round index for last round was 23)
    rc = 23
    A = iotainverse(A, rc, w)
    A = ChiInverse(A, w)
    A = piInverse(A, w)
    A = rhoInverse(A, w)

    # Now A is State 3, Fig 9
    # print(A)
    # 8 groups of 3 slices
    slices3groups = []
    for i in range(0, 24, 3):
        slices3groups.append( slices3(A, i) )
    
    slices6groups = []
    for i in range(0, 24, 6):
        slice3_0 = slices3groups[i//3]
        slice3_1 = slices3groups[i//3 + 1]
        slices6groups.append( merge3slices(A, i, slice3_0, slice3_1) )

    # deallocate memory from slices3groups
    del slices3groups # or
    slices3groups = None
