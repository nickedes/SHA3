from main import *

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
        y, x = x, (2*y + 3*x) % 5

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
                A_[y][x][z] = A[x % 5][(2*y + 3*x) % 5][z]
    # print("After pi")
    # printformat(getString(A_, w))
    # input()
    return A_

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
    """
    [a3, a9, a4, a2, a8, a7, a0, a5, a10, a1, a6] = bits
    slicei = [[a3, a7, a10, 0, 0], [0, a6, a9, 0, 0], [a2, a5, 0, 0, 0], [a1, a4, a8, 0, 0], [a0, 0, 0, 0, 0]]
    return slicei


solutions = [[12, [0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0], [0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0], [1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1], [1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0], [0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1], [1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1], [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1], [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1], [0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1], [1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0], [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0], [0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1], [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1], [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1], 62470]]

for solution in solutions:
    [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, slice15, phi14 ] = solution
    # construct state from slices
    Slices = [slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, slice15][::-1]
    w = len(Slices)
    for index, slicebits in enumerate(Slices):
        Slices[index] = getSlicefrombits(slicebits)
    Obtained_initialState = Construct_State(Slices)
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
