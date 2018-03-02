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


def getString(A):
    """
    A is the State array.
    The function returns the string representation for it.
    """

S = ""
for x in range(1600):
    S += str(x % 2)

print(getState(S, 64))
