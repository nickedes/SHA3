from math import log2


def getState(S, w):
    """
    S is the string of b bits.
    S denotes state for keccak_p permutation.
    This function returns the corresponding state array.
    """
    A = []
    for x in range(5):
        y_list = []
        for y in range(5):
            z_list = []
            for z in range(w):
                z_list.append(S[w*(5*y + x) + z])
                # A[x][y][z] = S[w*(5*y + x) + z]
            y_list.append(z_list)
        A.append(y_list)
    return A


def getString(A, w):
    """
    A is the State array.
    The function returns the string representation for it.
    """
    S = [0]*(25*w)
    for x in range(5):
        for y in range(5):
            for z in range(w):
                S[w*(5*y + x) + z] = str(A[x][y][z])

    return "".join(S)


def theta(A, w):
    """
    Theta Step mapping
    """
    C = [[0 for z in range(w)] for x in range(5)]
    for x in range(5):
        for z in range(w):
            C[x][z] = int(A[x][0][z]) ^ int(A[x][1][z]) ^ \
                int(A[x][2][z]) ^ int(A[x][3][z]) ^ int(A[x][4][z])
    D = [[0 for z in range(w)] for x in range(5)]
    for x in range(5):
        for z in range(w):
            D[x][z] = C[(x-1) % 5][z] ^ C[(x+1) % 5][(z-1) % w]

    A_ = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]

    for x in range(5):
        for y in range(5):
            for z in range(w):
                A_[x][y][z] = str(int(A[x][y][z]) ^ D[x][z])

    return A_


def rho(A, w):
    """
    rho step mapping - Rotate the bits of each lane by an offset.
    """
    # init for A_ ?
    A_ = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    for z in range(w):
        A_[0][0][z] = A[0][0][z]
    x, y = 1, 0
    for t in range(24):
        for z in range(w):
            A_[x][y][z] = A[x][y][(z - (t+1)*(t+2)//2) % w]
        x, y = y, (2*x + 3*y) % w
    return A_


def pi(A, w):
    """
    pi step mapping - Rearrange the positions of the lanes
    """
    A_ = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]

    for x in range(5):
        for y in range(5):
            for z in range(w):
                A_[x][y][z] = A[(x + 3*y) % 5][x][z]
    return A_


def chi(A, w):
    """
    Chi step mapping - XOR each bit with Non linear operation of two other bits in the same row
    """
    A_ = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    for x in range(5):
        for y in range(5):
            for z in range(w):
                A_[x][y][z] = str(int(A[x][y][z]) ^ (
                    (int(A[(x+1) % 5][y][z]) ^ 1) & int(A[(x+2) % 5][y][z])))
    return A_


def rc(t):
    """
    Round constant for iota step mapping
    """
    if t % 255 == 0:
        return 1
    R = [1, 0, 0, 0, 0, 0, 0, 0]
    for i in range(1, t % 255):
        R = [0] + R
        R[0] = R[0] ^ R[8]
        R[4] = R[4] ^ R[8]
        R[5] = R[5] ^ R[8]
        R[6] = R[6] ^ R[8]
        R = trunc(R, 8)
    return R[0]


def iota(A, i, w):
    """
    Iota step mapping - modify some bits of (0, 0) Lane based on round constant
    """
    A_ = [[[A[x][y][z] for z in range(w)] for y in range(5)] for x in range(5)]
    RC = [0]*w
    l = int(log2(w))
    for j in range(l+1):
        RC[2**j - 1] = rc(j + 7*i)

    for z in range(w):
        A_[0][0][z] = str(int(A_[0][0][z]) ^ RC[z])
    return A_


def round(A, i, w):
    """
    A - state
    i - round index
    """
    return iota(chi(pi(theta(A, w), w), w), i, w)


def keccak_p(S, nr):
    """
    """
    w = len(S)//25
    l = int(log2(w))
    A = getState(S, w)
    for i in range(12+2*l - nr, 12 + 2*l):
        A = round(A, i, w)
    S = getString(A, w)
    return S


def keccak_f(S):
    """
    """
    b = len(S)
    w = b//25
    l = int(log2(w))
    return keccak_p(S, 12 + 2*l)


def trunc(S, r):
    """
    """
    return S[:r]


def pad(x, m):
    """
    """
    j = (- m - 2) % x
    return '1'+'0'*j+'1'


def sponge(N, r, d):
    """
    Input : String N
    Output size of d bits
    """
    P = N + pad(r, len(N))
    n = len(P)//r
    b = 1600
    c = b - r
    S = '0'*b
    for i in range(n):
        format_spec = "{:0"+str(len(S))+"b}"
        S_ = format_spec.format(int(S, 2) ^
                                int(P[i*r:(i+1)*r] + '0'*c, 2))
        S = keccak_f(S_)
    Z = ''
    while True:
        Z = Z + trunc(S, r)
        if d <= len(Z):
            return trunc(Z, d)
        S = keccak_f(S)


def Keccak_c(c, N, d):
    """
    """
    return sponge(N, 1600-c, d)


def SHA3_d(M, d):
    """
    Generic method for four SHA-3 hash functions
    d : digest length
    """
    return Keccak_c(2*d, M+"01", d)


def RawSHAKEc(c, J, d):
    """
    """
    return Keccak_c(2*c, J+"11", d)


def SHAKEc(c, M, d):
    """
    """
    return RawSHAKEc(c, M+"11", d)


# w = 64

# b = 25*w

# # S = ""
# S = []
# for x in range(b):
#     # S += str(x % 2)
#     S += [x]
# A = getState(S, w)
# print(getString(A, w))

d = 224
l = SHA3_d("", d)

print(l)
r = 1600 - 2*d

print()
