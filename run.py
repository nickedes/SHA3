from main import *

def rhoInverse(A, w):
    """
    rho step mapping - Rotate the bits of each lane by an offset.
    """
    # ToDo : check, still rhoInverse fixed
    A_ = [[[ 0 for z in range(w)] for y in range(5)] for x in range(5)]

    rhoOffsets = [[0, 36, 3, 105, 210], [1, 300, 10, 45, 66], [190, 6, 171, 15, 253], [28, 55, 153, 21, 120], [91, 276, 231, 136, 78]]
    for x in range(5):
        for y in range(5):
            for z in range(w):
                A_[x][y][z] = A[x][y][(z - rhoOffsets[x][y] ) % w]
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

def picords(lane):
    """
    """
    x, y = lane
    return (y, (2*x + 3*y) % 5)


def Construct_State(Slices):
    """
        Construct a state of Keccak from the given slices
    """
    w = len(Slices)
    A = [ [ [0 for z in range(w)] for y in range(5) ] for x in range(5) ]
    for index, slicei in enumerate(Slices):
        # index is the Slice number
        for x in range(5):
            for y in range(5):
                # update the slice
                A[x][y][index] = slicei[x][y]
    return A


def getSlicefrombits(bits):
    """
        Construct slice from state bits
    """
    [a3, a9, a4, a2, a8, a7, a0, a5, a10, a1, a6] = bits
    state_slice = [ [ a3, 0, a2, a1, a0 ], [ a7, a6, a5, a4, 0], [ a10, a9, 0, a8, 0], [ 0, 0, 0, 0, 0], [ 0, 0, 0, 0, 0] ]
    return state_slice

# 34c63d2d5a8e4b30e3ebccaf
solutions = [[15, [1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1], [0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0], [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0], [1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1], [0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1], [0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1], [1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1], [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1], [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0], [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0], [1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0], 29410]]

for solution in solutions:
    [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, slice15, phi14 ] = solution
    # construct state from slices
    Slices = [slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, slice15]
    w = len(Slices)
    for index, slicebits in enumerate(Slices):
        Slices[index] = getSlicefrombits(slicebits)
    Obtained_SecondState = Construct_State(Slices)
    Obtained_initialState = rhoInverse( piInverse(Obtained_SecondState, w), w)


    print("===================Initial Checks : ===========================")
    # these lanes should be (0)
    zerolanes = [(0,3), (0,4), (1,3), (1,4), (2,3), (2,4), (3,2), (3,3), (3,4), (4,2), (4,3), (4,4)]

    print("===============================================================")
    for lane in zerolanes:
        x,y = lane
        for z in range(w):
            if Obtained_initialState[x][y][z] != 0:
                print(lane, " lane is not zero")
                break

    print("=================== Theta Check : ===========================")
    afterTheta_State = theta(Obtained_initialState, w)
    for x in range(5):
        for y in range(5):
            for z in range(w):
                if afterTheta_State[x][y][z] != Obtained_initialState[x][y][z]:
                    print("Bit MisMatch : ", (x, y , z))
    if afterTheta_State == Obtained_initialState:
        print("Pass!")
    else:
        print("theta Check failed!!")
        # exit()
    print("===============================================================")
    msg = getString(Obtained_initialState, w)
    print("msg : " , msg)
    state_size = 400
    # r + c = state_size
    # c bits
    c = 192
    # r bits
    r = state_size - c
    d = c//2
    # msg = getString(state, w)
    # print(msg)
    l = int(log2(w))
    A = Obtained_initialState
    nr = 2
    for i in range(12+2*l - nr, 12 + 2*l):
        A = round(A, i, w)
    S = getString(A, w)
    Z = ''
    while True:
        Z = Z + trunc(S, r)
        if d <= len(Z):
            break
        S = keccak_p(S, nr)
    S = trunc(Z, d)
    # digest = "100000000000000000000000"
    print("digest : ", S)
    printformat(S)

# Next steps :
# 1. Change implementation of rho and rhoInverse, should be similar to the one taken in attack
# 2. observe the attack after above changes
