def getState(S, w):
    """
    S is the string of b bits.
    S denotes state for keccak permutation.
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
            C[x][z] = A[x][0][z] ^ A[x][1][z] ^ \
                A[x][2][z] ^ A[x][3][z] ^ A[x][4][z]
    D = [[0 for z in range(w)] for x in range(5)]
    for x in range(5):
        for z in range(w):
            D[x][z] = C[(x-1) % 5][z] ^ C[(x+1) % 5][(z-1) % w]

    A_ = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]

    for x in range(5):
        for y in range(5):
            for z in range(w):
                A_[x][y][z] = A[x][y][z] ^ D[x][z]

    return A_


w = 64

b = 25*w

# S = ""
S = []
for x in range(b):
    # S += str(x % 2)
    S += [x]
A = getState(S, w)
print(getString(A, w))
