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