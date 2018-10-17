from main import *


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
            else
                A = slice2
            C[x][z] = A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4]

    D = [[0 for z in range(2)] for x in range(5)]

    for x in range(5):
        z = 1
        D[x][z] = C[(x-1) % 5][z] ^ C[(x+1) % 5][(z-1) % 2]

    A_ = [[[0 for z in range(2)] for y in range(5)] for x in range(5)]

    for x in range(5):
        for y in range(5):
            z = 1
            A = slice1
            A_[x][y][z] = A[x][y] ^ D[x][z]
    return A_

def check( slice0, slice1, A, i):
    """
    """
    slice0 = applyChi(slice0)
    slice1 = applyChi(slice1)

    state = applytheta(slice0, slice1)



def slices3(A, i):
    """
    """
    for a00 in range(2):
        for a01 in range(2):
                for a10 in range(2):
                    for a11 in range(2):
                            for a20 in range(2):
                                for a21 in range(2):
                                        for b00 in range(2):
                                            for b01 in range(2):
                                                    for b10 in range(2):
                                                        for b11 in range(2):
                                                                for b20 in range(2):
                                                                    for b21 in range(2):
                                                                            for c00 in range(2):
                                                                                for c01 in range(2):
                                                                                        for c10 in range(2):
                                                                                            for c11 in range(2):
                                                                                                    for c20 in range(2):
                                                                                                        for c21 in range(2):
                                                                                                                for e00 in range(2):
                                                                                                                    for e01 in range(2):
                                                                                                                            for e10 in range(2):
                                                                                                                                for e11 in range(2):
                                                                                                                                    # Check these 22 variables first
                                                                                                                                    slice0 = [ [a00, b20, c20, 0, 0], [0, e10, a10, 0, 0], [b00, c10, 0, 0, 0], [e00, a20, b10, 0, 0], [c00, 0, 0, 0, 0]]
                                                                                                                                    slice1 = [ [a01, b21, c21, 0, 0], [0, e11, a11, 0, 0], [b01, c11, 0, 0, 0], [e01, a21, b11, 0, 0], [c01, 0, 0, 0, 0]]

                                                                                                                                    result = check( slice0, slice1, A, i + 1)

                                                                                                                                    if result:
                                                                                                                                        for a02 in range(2):
                                                                                                                                            for a12 in range(2):
                                                                                                                                                for a22 in range(2):
                                                                                                                                                    for b02 in range(2):
                                                                                                                                                        for b12 in range(2):
                                                                                                                                                            for b22 in range(2):
                                                                                                                                                                for c02 in range(2):
                                                                                                                                                                    for c12 in range(2):
                                                                                                                                                                        for c22 in range(2):
                                                                                                                                                                                for e02 in range(2):
                                                                                                                                                                                    for e12 in range(2):



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
    print(A)
