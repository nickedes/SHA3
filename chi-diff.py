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
