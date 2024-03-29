from main import *
import itertools
import multiprocessing as mp


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


def getslicebits(slicei):
    [[a3, a7, a10, _, _], [d0, a6, a9, _, _], [a2, a5, _, _, _], [a1, a4, a8, _, _], [a0, d1, _, _, _]] = slicei
    slicein = [a3, a9, a4, a2, a8, a7, a0, a5, a10, a1, a6]
    return slicein


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

    if i == 1:
        slice0[0][0] = slice0[0][0] ^ 1

    if i == 0:
        slice1[0][0] = slice1[0][0] ^ 1

    if slicei[0][0] == A[0][0][i] and slicei[1][1] == A[1][1][i] and slicei[2][2] == A[2][2][i] and slicei[3][3] == A[3][3][i] and slicei[4][4] == A[4][4][i] and slicei[3][0] == A[3][0][i] and slicei[4][1] == A[4][1][i]:
        return True
    return False


def paritychecker( A, i, slicei):
    """
        Checks and find the parity for previous slice based on the ith slice
    """
    slicei = applyChi(slicei)
    if i == 0:
        slicei[0][0] = slicei[0][0] ^ 1
    # parity
    c = [0 for x in range(5)]
    for x in range(5):
        c[x] = slicei[x][0] ^ slicei[x][1] ^ slicei[x][2] ^ slicei[x][3] ^ slicei[x][4]
    # prev slice parity
    d = [ 0, 0, 0, 0, 0, 0, 0]
    d[0] = A[0][0][i] ^ slicei[0][0] ^ c[1]
    d[1] = A[1][1][i] ^ slicei[1][1] ^ c[2]
    d[2] = A[2][2][i] ^ slicei[2][2] ^ c[3]
    d[3] = A[3][3][i] ^ slicei[3][3] ^ c[4]
    d[4] = A[4][4][i] ^ slicei[4][4] ^ c[0]
    
    if d[3] == A[3][0][i] ^ slicei[3][0] ^ c[4] and d[4] == A[4][1][i] ^ slicei[4][1] ^ c[0]:
        phi1 = d[0] + 2*d[1] + 4*d[2] + 8*d[3] + 16*d[4]
        phi2 = c[0] + 2*c[1] + 4*c[2] + 8*c[3] + 16*c[4]
        d[5] = phi1
        d[6] = phi2
        return d
    return []



def slices3(A, ind, output):
    """
    """
    # values for slice2
    values2 = []
    for a0_2, a1_5, a2_6, b0_3, b1_12, b2_14, c0_0, c1_8, c2_13, e0_13, e1_6 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
        slice2 = [ [a0_2, b2_14, c2_13, 0, 0], [0, e1_6, a1_5, 0, 0], [b0_3, c1_8, 0, 0, 0], [e0_13, a2_6, b1_12, 0, 0], [c0_0, 0, 0, 0, 0]]
        parity = paritychecker(A, ind + 2, slice2)
        if len(parity) == 7:
            values2.append([ parity, [a0_2, a1_5, a2_6, b0_3, b1_12, b2_14, c0_0, c1_8, c2_13, e0_13, e1_6] ])

    values1 = []
    for a0_1, a1_4, a2_5, b0_2, b1_11, b2_13, c0_15, c1_7, c2_12, e0_12, e1_5 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
        slice1 = [ [a0_1, b2_13, c2_12, 0, 0], [0, e1_5, a1_4, 0, 0], [b0_2, c1_7, 0, 0, 0], [e0_12, a2_5, b1_11, 0, 0], [c0_15, 0, 0, 0, 0]]
        parity = paritychecker(A, ind + 1, slice1)
        if len(parity) == 7:
            values1.append([ parity, [a0_1, a1_4, a2_5, b0_2, b1_11, b2_13, c0_15, c1_7, c2_12, e0_12, e1_5] ])

    #  phi1 of slice1 in parity pos 6
    values1 = sorted(values1, key=lambda x : x[0][6] )
    
    #  phi1 of slice2 in parity pos 5
    values2 = sorted(values2, key=lambda x : x[0][5] )
    
    values = []

    n = len(values1)
    m = len(values2)


    prev_i = 0
    prev_j = 0

    next_i = n
    next_j = m
    
    i = 0
    j = 0
    print(n)
    print(m)
    flag = 1
    print("=============================================== Merging ================================================")

    
    while flag == 1:
        i = prev_i
        j = prev_j
        while i + 1 < n:
            if values1[i][0][6] < values1[i + 1][0][6]:
                break
            i= i + 1
        next_i = i +1    
        while j + 1 < m:
            if values2[j][0][5] < values2[j + 1][0][5]:
                break
            j= j + 1
        next_j = j + 1    
          
        if values1[prev_i][0][6] == values2[prev_j][0][5]:
            i = prev_i
            j = prev_j
            while i < next_i:
                while j < next_j:

                    parity = [ values1[i][0][0], values1[i][0][1], values1[i][0][2], values1[i][0][3] , values1[i][0][4], values1[i][0][5] ]
                    # phi2
                    parity.append( values2[j][0][6] )

                    values.append( [  parity, values1[0][1], values2[0][1] ] )
                    j+=1
                i+=1
                j = prev_j
            prev_i = next_i
            prev_j = next_j
            #print("equal")
            #print(prev_i)
            #print(next_i)
            #print(prev_j)
            #print(next_j)
        elif values1[prev_i][0][6] > values2[prev_j][0][5]:
            prev_j = next_j
        else:
            prev_i = next_i

        if prev_i < n and prev_j < m:
            flag = 1
        else:
            flag = 0
        #print("prev i and prev j")    
        #print(prev_i)
        #print(prev_j)
        #print(next_i)
        #print(next_j)        
    print("=============================================== Merging Done================================================")
        
    output.put((ind,values))


def slices6(A, ind, values1, values2, output):
    """
    """
    d0 = 0
    d1 = 0
    list3 = {}
    solution3 = []
    for phi3 in range(0, 32):
        c0 = phi3 % 2
        t = phi3
        t = t//2
        c1 = t % 2
        t = t//2
        c2 = t % 2
        t = t//2
        c3 = t % 2
        t = t//2
        c4 = t % 2
        for a1, a2, a3, a4, a5, a6, a7, a9, a10 in itertools.product(range(2), range(2), range(2), range(2), range(2), range(2), range(2), range(2), range(2)): 
            a0 = c3 ^ a1 ^ a2 ^ a3 ^ d0
            a8 = c2 ^ a9 ^ a10
            # add iota
            if ( c0 == a0 ^ a1 ^ a2 ^ a3 ^ ((a4 ^ 1)*a8) ^ ((a6 ^ 1)*a9) ^ ((a7 ^ 1)*a10) ^ d0 ) and ( c1 == a4 ^ a5 ^ a6 ^ a7 ^ d1 ) and ( c4 == (a1 ^ 1)*a4 ^ (a2 ^ 1)*a5 ^ (a0 ^ 1)*d1 ^ (d0 ^ 1)*a6 ^ (a3 ^ 1)*a7 ):
                slice3 = [[a3, a7, a10, 0, 0], [d0, a6, a9, 0, 0], [a2, a5, 0, 0, 0], 
                [a1, a4, a8, 0, 0], [a0, d1, 0, 0, 0]]
                parity = paritychecker( A, ind + 3, slice3)
                slice3in = [a3, a9, a4, a2, a8, a7, a0, a5, a10, a1, a6]
                if len(parity) > 0:
                    phi2 = parity[5]
                    if phi3 not in list3:
                        list3[phi3] = [ [phi2, slice3in] ]
                    else:
                        list3[phi3].append([phi2, slice3in])
    for val in values2:
        phi3 = val[0][5]
        phi5 = val[0][6]
        phi3list = list3[phi3]
        slice4 = val[1]
        slice5 = val[2]
        for x in phi3list:
            slice3 = x[1]
            phi2 = x[0] + (2**5)*(slice4[0]) + (2**6)*slice5[0]
            solution3.append([phi2, slice3, slice4, slice5, phi5])
    values2 = None
    solution3 = sorted(solution3, key =lambda x : x[0])

    list0 = {}
    solution0 = []
    d0 = 0
    d1 = 0
    for phi0 in range(0, 32):
        c0 = phi0 % 2
        t = phi0
        t = t//2
        c1 = t % 2
        t = t//2
        c2 = t % 2
        t = t//2
        c3 = t % 2
        t = t//2
        c4 = t % 2
        for a1, a2, a3, a4, a5, a6, a7, a9, a10 in itertools.product(range(2), range(2), range(2), range(2), range(2), range(2), range(2), range(2), range(2)): 
            a0 = c3 ^ a1 ^ a2 ^ a3 ^ d0
            a8 = c2 ^ a9 ^ a10
            # add iota
            iota = 0
            if ind == 0:
                iota = 1
            if ( c0 == a0 ^ a1 ^ a2 ^ a3 ^ ((a4 ^ 1)*a8) ^ ((a6 ^ 1)*a9) ^ ((a7 ^ 1)*a10) ^ d0 ^ iota ) and ( c1 == a4 ^ a5 ^ a6 ^ a7 ^ d1 ) and ( c4 == (a1 ^ 1)*a4 ^ (a2 ^ 1)*a5 ^ (a0 ^ 1)*d1 ^ (d0 ^ 1)*a6 ^ (a3 ^ 1)*a7 ):
                slice0 = [[a3, a7, a10, 0, 0], [d0, a6, a9, 0, 0], [a2, a5, 0, 0, 0], [a1, a4, a8, 0, 0], [a0, d1, 0, 0, 0]]
                parity = paritychecker( A, ind, slice0)
                if len(parity) > 0:
                    phi15 = parity[5]
                    slice0in = getslicebits(slice0)
                    if phi0 not in list0:
                        list0[phi0] = [ [phi15, slice0in] ]
                    else:
                        list0[phi0].append([phi15, slice0in])

    for val in values1:
        phi0 = val[0][5]
        phi2 = val[0][6]
        phi0list = list0[phi0]
        slice1 = val[1]
        slice2 = val[2]
        for x in phi0list:
            slice0 = x[1]
            phi2 = phi2 + (2**5)*(slice0[2] ^ slice1[1]) + (2**6)*(slice1[2] ^ slice2[1])
            solution0.append([phi15, slice0, slice1, slice2, phi2])
    values1 = None
    solution0 = sorted(solution0, key =lambda x : x[4])

    # Todo : Merging
    values = []

    n = len(solution0)
    m = len(solution3)


    prev_i = 0
    prev_j = 0

    next_i = n
    next_j = m
    
    i = 0
    j = 0

    flag = 1
    
    while flag == 1:
        i =  prev_i
        j = prev_j
        while i + 1 < n:
            if solution0[i][4] < solution0[i + 1][4]:
                break
            i = i + 1   
        next_i = i + 1    
        while j + 1 < m:
            if solution3[j][0] < solution3[j + 1][0]:
                break
            j = j + 1
        next_j = j + 1        

        if solution0[prev_i][4] == solution3[prev_j][0]:
            i = prev_i
            j = prev_j
            while i < next_i:
                while j < next_j:
                    [phi15, slice0, slice1, slice2, phi2] = solution0[i]
                    [phi2_ , slice3, slice4, slice5, phi5] = solution3[j]
                    values.append( [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, phi5 ] )
                    j+=1
                i+=1
                j=prev_j
            prev_i = next_i
            prev_j = next_j
        elif solution0[prev_i][4] > solution3[prev_j][0]:
            prev_j = next_j
        else:
            prev_i = next_i

        if prev_i < n and prev_j < m:
            flag = 1
        else:
            flag = 0
    output.put((ind,values))


def slices12(A, ind, values1, values2, output):
    """
    """
    # modify phi5
    for i in range(len(values1)):
        [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, phi5 ] = values1[i]
        phi5 = phi5 + (2**5)*(slice3[1] ^ slice2[2]) + (2**6)*(slice4[1] ^ slice3[2]) + (2**7)*(slice5[1] ^ slice4[2]) + (2**8)*(slice5[2]) + (2**9)*(slice2[4] + slice0[5]) + (2**10)*(slice0[3] ^ slice5[5]) + (2**11)*(slice1[3]) + (2**12)*(slice2[3]) + (2**13)*(slice3[3]) + (2**14)*(slice4[3]) + (2**15)*(slice0[6] ^ slice3[8]) + (2**16)*(slice1[6] ^ slice4[8]) + (2**17)*(slice2[6] ^ slice5[8]) + (2**18)*(slice3[6]) + (2**19)*(slice0[7]) + (2**20)*(slice0[10]) + (2**21)*(slice1[10]) + (2**22)*(slice2[10])
        values1[i][7] = phi5
    for i in range(len(values2)):
        [ phi5, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] = values2[i]
        phi5 = phi5 + (2**5)*(slice6[0]) + (2**6)*(slice7[0]) + (2**7)*(slice8[0]) + (2**8)*(slice9[0]^slice6[1]) + (2**9)*(slice11[3]) + (2**10)*(slice7[4]) + (2**11)*(slice8[4] ^ slice6[5]) + (2**12)*(slice9[4] ^ slice7[5]) + (2**13)*(slice10[4] ^ slice8[5]) + (2**14)*(slice11[4] ^ slice9[5]) + (2**15)*(slice8[7]) +          (2**16)*(slice9[7]) + (2**17)*(slice10[7]) + (2**18)*(slice10[7] ^ slice6[8]) + (2**19)*(slice8[6] ^ slice11[8]) + (2**20)*(slice9[9]) + (2**21)*(slice10[9]) + (2**22)*(slice11[9])
        values2[i][0] = phi5
    values1 = sorted(values1, key = lambda x : x[7])
    values2 = sorted(values2, key = lambda x : x[0])
    # Todo : Merging
    values = []

    n = len(values1)
    m = len(values2)


    prev_i = 0
    prev_j = 0

    next_i = n
    next_j = m
    
    i = 0
    j = 0

    flag = 1
    
    while flag == 1:
        i =  prev_i
        j = prev_j
        while i + 1 < n:
            if values1[i][7] < values1[i + 1][7]:
                break
            i = i + 1
        next_i = i + 1        

        while j + 1 < m:
            if values2[j][0] < values2[j + 1][0]:
                break
            j = j + 1
        next_j = j + 1        

        if values1[prev_i][7] == values2[prev_j][0]:
            i = prev_i
            j = prev_j
            while i < next_i:
                while j < next_j:
                    [ phi15, slice0, slice1, slice2, phi2, slice3, slice4, slice5, phi5 ] = values1[i]
                    [ phi5_, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] = values2[j]
                    values.append( [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] )
                    j+=1
                i+=1
                j=prev_j
            prev_i = next_i
            prev_j = next_j
        elif values1[prev_i][7] > values2[prev_j][0]:
            prev_j = next_j
        else:
            prev_i = next_i

        if prev_i < n and prev_j < m:
            flag = 1
        else:
            flag = 0
    output.put((ind,values))


def slices15(A, ind, values1, values2, output):
    """
        values1 - 0 to 11 slices
        values2 - 12 to 14
    """
    d0 = 0
    d1 = 0
    list3 = {}
    solution3 = []
    for phi3 in range(0, 32):
        c0 = phi3 % 2
        t = phi3
        t = t//2
        c1 = t % 2
        t = t//2
        c2 = t % 2
        t = t//2
        c3 = t % 2
        t = t//2
        c4 = t % 2
        for a1, a2, a3, a4, a5, a6, a7, a9, a10 in itertools.product(range(2), range(2), range(2), range(2), range(2), range(2), range(2), range(2), range(2)): 
            a0 = c3 ^ a1 ^ a2 ^ a3 ^ d0
            a8 = c2 ^ a9 ^ a10
            # add iota
            if ( c0 == a0 ^ a1 ^ a2 ^ a3 ^ ((a4 ^ 1)*a8) ^ ((a6 ^ 1)*a9) ^ ((a7 ^ 1)*a10) ^ d0 ) and ( c1 == a4 ^ a5 ^ a6 ^ a7 ^ d1 ) and ( c4 == (a1 ^ 1)*a4 ^ (a2 ^ 1)*a5 ^ (a0 ^ 1)*d1 ^ (d0 ^ 1)*a6 ^ (a3 ^ 1)*a7 ):
                slice12 = [[a3, a7, a10, 0, 0], [d0, a6, a9, 0, 0], [a2, a5, 0, 0, 0], [a1, a4, a8, 0, 0], [a0, d1, 0, 0, 0]]
                parity = paritychecker( A, ind + 12, slice12)
                if len(parity) > 0:
                    phi11 = parity[5]
                    slice12in = getslicebits(slice12)
                    if phi3 not in list3:
                        list3[phi3] = [ [phi11, slice12in] ]
                    else:
                        list3[phi3].append([phi11, slice12in])
    for val in values2:
        phi12 = val[0][5]
        phi14 = val[0][6]
        phi3list = list3[phi12]
        slice13 = val[1]
        slice14 = val[2]
        for x in phi3list:
            slice12 = x[1]
            phi11 = x[0] + (2**5)*slice12[0] + (2**6)*slice13[0] + (2**7)*slice14[0] + (2**8)*(slice12[2] ^ slice13[1]) + (2**9)*(slice13[2] ^ slice14[2]) + (2**10)*(slice12[4]) + (2**11)*(slice13[4])\
                    + (2**12)*(slice14[4] ^ slice12[5]) + (2**13)*slice14[5] + (2**14)*slice12[3] + (2**15)*slice12[4] + (2**16)*slice12[5] + (2**17)*slice12[8] + (2**18)*slice13[8]\
                    + (2**19)*(slice14[8]) + (2**20)*slice13[6] + (2**21)*slice14[6] + (2**22)*slice12[7] + (2**23)*slice13[7] + (2**24)*slice14[7] + (2**25)*slice12[9] + (2**26)*slice13[9]\
                    + (2**27)*(slice14[9]) + (2**28)*slice12[10] + (2**29)*slice13[10] + (2**30)*slice14[10]
            solution3.append([phi11, slice12, slice13, slice14, phi14])
    values2 = None
    values2 = sorted(solution3, key =lambda x : x[0])
    solution3 = None

    for i in range(len(values1)):
        [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] = values1[i]
        phi11 = phi11 + (2**5)*(slice9[1] ^ slice8[2]) + (2**6)*(slcie10[1] ^ slice9[2]) + (2**7)*(slice11[1] ^ slice10[2]) + (2**8)*(slice0[0]) + (2**9)*slice1[0] + (2**10)*(slice5[3] ^ slice10[5])\
                + (2**11)*(slice6[3] ^ slice11[5]) + (2**12)*slcie7[3] + (2**13)*(slice0[4] ^ slice9[0]) + (2**14)*(slice3[4] ^ slice1[5]) + (2**15)*(slice4[4] ^ slice2[5])\
                + (2**16)*(slice5[4] ^ slice3[5]) + (2**17)*(slice9[6] ^ slice1[7]) + (2**18)*(slice10[6] ^ slice2[7]) + (2**19)*(slice11[6] ^ slice3[7]) + (2**20)*(slice0[8] ^ slice5[7])\
                + (2**21)*(slice1[8] ^ slice6[7]) + (2**22)*(slice7[8] ^ slice4[6]) + (2**23)*(slice8[8] ^ slice5[6]) + (2**24)*(slice9[8] ^ slice6[6]) + (2**25)*(slice3[10]) + (2**26)*(slice4[10])\
                + (2**27)*slice5[10] + (2**28)*slice5[9] + (2**29)*slice6[9] + (2**30)*(slice7[9])
        values1[i][13] = phi11

    values1 = sorted(values1, key = lambda x : x[13])
    values = []

    n = len(values1)
    m = len(values2)


    prev_i = 0
    prev_j = 0

    next_i = n
    next_j = m
    
    i = 0
    j = 0

    flag = 1
    
    while flag == 1:
        i =  prev_i
        j = prev_j
        while i + 1 < n:
            if values1[i][13] < values1[i + 1][13]:
                break
            i = i + 1
        next_i = i + 1        

        while j + 1 < m:
            if values2[j][0] < values2[j + 1][0]:
                break
            j = j + 1
        next_j = j + 1        

        if values1[prev_i][13] == values2[prev_j][0]:
            i = prev_i
            j = prev_j
            while i < next_i:
                while j < next_j:
                    [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] = values1[i]
                    [ phi11_, slice12, slice13, slice14, phi14 ] = values2[j]
                    values.append( [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, phi14 ] )
                    j+=1
                i+=1
                j=prev_j
            prev_i = next_i
            prev_j = next_j
        elif values1[prev_i][13] > values2[prev_j][0]:
            prev_j = next_j
        else:
            prev_i = next_i

        if prev_i < n and prev_j < m:
            flag = 1
        else:
            flag = 0
    output.put((ind,values))


def slices16(A, ind, values1, output):
    """
    """
    # values for slice2
    values2 = []
    for a0_2, a1_5, a2_6, b0_3, b1_12, b2_14, c0_0, c1_8, c2_13, e0_13, e1_6 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
        slice2 = [ [a0_2, b2_14, c2_13, 0, 0], [0, e1_6, a1_5, 0, 0], [b0_3, c1_8, 0, 0, 0], [e0_13, a2_6, b1_12, 0, 0], [c0_0, 0, 0, 0, 0]]
        parity = paritychecker(A, ind + 15, slice2)
        if len(parity) == 7:
            phi14 = parity[5]
            phi15 = parity[6]
            phi14 = phi14 + (2**5)*a0_2 + (2**6)*a1_5 + (2**7)*a2_6 + (2**8)*b0_3 + (2**9)*b1_12 + (2**10)*b2_14 + (2**11)*c0_0 + (2**12)*c1_8 + (2**13)*c2_13 + (2**14)*e0_13 + (2**15)*e1_6
            values2.append([ phi14, phi15, [a0_2, a1_5, a2_6, b0_3, b1_12, b2_14, c0_0, c1_8, c2_13, e0_13, e1_6] ])
    for i in range(len(values1)):
        [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, phi14 ] = values1[i]
        phi14 = phi14 + (2**5)*(slice12[1] ^ slice11[2]) + (2**6)*(slice2[0] ^ slice14[2]) + (2**7)*(slcie0[1] ^ slice3[0]) + (2**8)*(slice6[4] ^ slice4[5]) + (2**9)*(slice8[3] ^ slice13[5]) + (2**10)*(slice10[3] ^ slice1[4]) + (2**11)*(slice7[7] ^ slice2[8]) + (2**12)*(slice7[7] ^ slice10[8]) + (2**13)*(slice12[6] ^ slice4[7]) + (2**14)*(slice6[10]) + (2**15)*(slice8[9])
        values1[i][16] = phi14
            
    # sort on phi14
    values1 = sorted(values1, key = lambda x : x[16])
        
    values2 = sorted(values2, key = lambda x : x[0])
    values = []

    n = len(values1)
    m = len(values2)


    prev_i = 0
    prev_j = 0

    next_i = n
    next_j = m
    
    i = 0
    j = 0

    flag = 1
    
    while flag == 1:
        i =  prev_i
        j = prev_j
        while i + 1 < n:
            if values1[i][16] < values1[i + 1][16]:
                break
            i = i + 1
        next_i = i + 1        

        while j + 1 < m:
            if values2[j][0] < values2[j + 1][0]:
                break
            j = j + 1
        next_j = j + 1        

        if values1[prev_i][16] == values2[prev_j][0]:
            i = prev_i
            j = prev_j
            while i < next_i:
                while j < next_j:
                    [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, phi14 ] = values1[i]
                    [ phi14_, phi15_, slice15 ] = values2[j]
                    if phi14 == phi14_ and phi15 == phi15_:
                        values.append( [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, phi14 ] )
                    j+=1
                i+=1
                j=prev_j
            prev_i = next_i
            prev_j = next_j
        elif values1[prev_i][16] > values2[prev_j][0]:
            prev_j = next_j
        else:
            prev_i = next_i

        if prev_i < n and prev_j < m:
            flag = 1
        else:
            flag = 0
    output.put((ind,values))


def slices2(A, i):
    """
    """
    values = []
    for a0_30, a0_31, a1_1, a1_2, a2_2, a2_3, b0_31, b0_0, b1_8, b1_9, b2_10, b2_11 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
        for c0_28, c0_29, c1_4, c1_5, c2_9, c2_10, e0_25, e0_26, e1_18, e1_19 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
            slice_30 = [ [a0_30, b2_10, c2_9, 0, 0], [0, e1_18, a1_1, 0, 0], [b0_31, c1_4, 0, 0, 0], [e0_25, a2_2, b1_8, 0, 0], [c0_28, 0, 0, 0, 0]]
            slice_31 = [ [a0_31, b2_11, c2_10, 0, 0], [0, e1_19, a1_2, 0, 0], [b0_0, c1_5, 0, 0, 0], [e0_26, a2_3, b1_9, 0, 0], [c0_29, 0, 0, 0, 0]]

            result = check( slice_30, slice_31, A, i + 1)
            if result:
                values.append([a0_30, a0_31, a1_1, a1_2, a2_2, a2_3, b0_31, b0_0, b1_8, b1_9, b2_10, b2_11, c0_28, c0_29, c1_4, c1_5, c2_9, c2_10, e0_25, e0_26, e1_18, e1_19])
    return values


def phi3_0(slice3_0i):
    """
    """
    [a0_0, a0_1, a0_2, a1_3, a1_4, a1_5, a2_4, a2_5, a2_6, b0_1, b0_2, b0_3, b1_10, b1_11, b1_12, b2_12, b2_13, b2_14, c0_14, c0_15, c0_0, c1_6, c1_7, c1_8, c2_11, c2_12, c2_13, e0_11, e0_12, e0_13, e1_4, e1_5, e1_6] = slice3_0i
    x = (a1_4 + a2_4) % 2
    y = (a1_5 + a2_5) % 2
    return x + y*2


def phi3_1(slice3_1i):
    """
    """
    [a0_3, a0_4, a0_5, a1_6, a1_7, a1_8, a2_7, a2_8, a2_9, b0_4, b0_5, b0_6, b1_13, b1_14, b1_15, b2_15, b2_0, b2_1, c0_1, c0_2, c0_3, c1_9, c1_10, c1_11, c2_14, c2_15, c2_0, e0_14, e0_15, e0_0, e1_7, e1_8, e1_9] = slice3_1i
    return a0_4 + 2*a0_5


def merge3slices(A, ind, slice3_0, slice3_1, output):
    """
    """
    values = []
    # sort1st by phi31 function
    slice3_0 = sorted(slice3_0, key=lambda x : phi3_0(x) )
    slice3_1 = sorted(slice3_1, key=lambda x : phi3_1(x) )

    n = len(slice3_0)
    m = len(slice3_1)

    prev_j = 0
    i = 0
    j = 0
    while i < n:
        a = phi3_0 ( slice3_0[i] )
        b = phi3_1 ( slice3_1[ prev_j ] )
        if a == b:
            j = prev_j
        elif a > b:
            prev_j += 1
            j = prev_j
        elif a < b:
            i+=1
        while j < m:
            if phi3_0 ( slice3_0[i] ) == phi3_1 ( slice3_1[j] ):
                [a0_0, a0_1, a0_2, a1_3, a1_4, a1_5, a2_4, a2_5, a2_6, b0_1, b0_2, b0_3, b1_10, b1_11, b1_12, b2_12, b2_13, b2_14, c0_14, c0_15, c0_0, c1_6, c1_7, c1_8, c2_11, c2_12, c2_13, e0_11, e0_12, e0_13, e1_4, e1_5, e1_6] = slice3_0[i]
                [a0_3, a0_4, a0_5, a1_6, a1_7, a1_8, a2_7, a2_8, a2_9, b0_4, b0_5, b0_6, b1_13, b1_14, b1_15, b2_15, b2_0, b2_1, c0_1, c0_2, c0_3, c1_9, c1_10, c1_11, c2_14, c2_15, c2_0, e0_14, e0_15, e0_0, e1_7, e1_8, e1_9] = slice3_1[j]

                slice2 = [ [a0_2, b2_14, c2_13, 0, 0], [0, e1_6, a1_5, 0, 0], [b0_3, c1_8, 0, 0, 0], [e0_13, a2_6, b1_12, 0, 0], [c0_0, 0, 0, 0, 0]]
                slice3 = [ [a0_3, b2_15, c2_14, 0, 0], [0, e1_7, a1_6, 0, 0], [b0_4, c1_9, 0, 0, 0], [e0_14, a2_7, b1_13, 0, 0], [c0_1, 0, 0, 0, 0]]

                result = check( slice2, slice3, A, ind + 3)
                # if output slice bits satisfied
                if result:
                    values.append([a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e1_4, e1_5, e1_6, e1_7, e1_8, e1_9])
                j+=1
            else:
                break
        i+=1
    output.put((ind,values))


def phi6_0(slice6_0i):
    """
    """
    [a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e1_4, e1_5, e1_6, e1_7, e1_8, e1_9] = slice6_0i
    return ((a1_6 + a2_6)%2) + 2*((a2_7 + a1_7)%2) + 4*((a2_8 + a1_8)%2) + 8*(a2_9) + 16*((b1_12 + b2_12) % 2) + 32*((b0_1 + b2_1) % 2) + 64*b0_2 + 128*b0_3 + 256*b0_4 + 512*b0_5 + 1024*c1_6 + 2048*((c0_14 + c2_14)%2) + (2**12)*((c0_15 + c2_15)%2) + (2**13)*((c0_0 + c2_0)%2) + (2**14)*(c0_1) + (2**15)*e1_4 + (2**16)*e1_5 + (2**17)*e0_11 + (2**18)*e0_12 + (2**19)*e0_13 + (2**20)*e0_14 + (2**21)*e0_15 + (2**22)*e1_6


def phi6_1(slice6_1i):
    """
    """
    [a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15] = slice6_1i
    return a0_6 + 2*(a0_7) + 4*(a0_8) + 8*((a1_9 + a0_9)%2) + 16*(b0_12) + 32*(b1_1) + 64*((b1_2 + b2_2)%2) + 128*((b1_3 + b2_3)%2) + 256*((b1_4 + b2_4)%2) + 512*((b1_5 + b2_5)%2) + 1024*((c0_6 + c2_6)%2) + 2048*(c1_14) + (2**12)*(c1_15) + (2**13)*(c1_0) + (2**14)*((c1_1 + c2_1)%2) + (2**15)*e0_4 + (2**16)*e0_5 + (2**17)*e1_11 + (2**18)*e1_12 + (2**19)*e1_13 + (2**20)*e1_14 + (2**21)*e1_15 + (2**22)*e0_6


def merge6slices(A, ind, slice6_0, slice6_1, output):
    """
    """
    values = []
    # sort1st by phi31 function
    slice6_0 = sorted(slice6_0, key=lambda x : phi6_0(x) )
    slice6_1 = sorted(slice6_1, key=lambda x : phi6_1(x) )

    n = len(slice6_0)
    m = len(slice6_1)

    values = []

    prev_j = 0
    i = 0
    j = 0
    while i < n:
        a = phi6_0 ( slice6_0[i] )
        b = phi6_1 ( slice6_1[ prev_j ] )
        if a == b:
            j = prev_j
        elif a > b:
            prev_j += 1
            j = prev_j
        elif a < b:
            i+=1
        while j < m:
            if phi6_0 ( slice6_0[i] ) == phi6_1 ( slice6_1[j] ):
                [a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e1_4, e1_5, e1_6, e1_7, e1_8, e1_9] = slice6_0[i]
                [a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15] = slice6_1[j]
                
                slice5 = [ [a0_5, b2_1, c2_0, 0, 0], [0, e1_9, a1_8, 0, 0], [b0_6, c1_11, 0, 0, 0], [e0_0, a2_9, b1_15, 0, 0], [c0_3, 0, 0, 0, 0]]
                slice6 = [ [a0_6, b2_2, c2_1, 0, 0], [0, e1_8, a1_9, 0, 0], [b0_7, c1_12, 0, 0, 0], [e0_1, a2_10, b1_0, 0, 0], [c0_4, 0, 0, 0, 0]]

                result = check( slice5, slice6, A, ind + 6)
                # if output slice bits satisfied
                if result:
                    values.append([a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7,
                        c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6,
                        e0_11, e0_12, e0_13, e0_14, e0_15, e0_0,  e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e1_4, e1_5, e1_6, e1_7, e1_8, e1_9, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15])
                j+=1
            else:
                break
        i+=1
    output.put((ind,values))


def phi12(slice12):
    """
    """
    [a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7,
                        c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6,
                        e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e1_4, e1_5, e1_6, e1_7, e1_8, e1_9, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15] = slice12

    return (a1_12 + a2_12)%2 + 2*((a1_13 + a2_13)%2) + 4*((a1_14 + a2_14)%2) + 8*(a0_0) + 16*(a0_1) + 32*((b0_6 + b2_6)%2) +64*((b0_7 + b2_7)%2) + 128*b0_8 + 256*((b0_10 + b1_10)%2) + 512*((b1_13 + b2_13)%2) + 1024*((b2_14 + b1_14)%2) + 2048*((b1_15 + b2_15)%2) + (2**12)*((c0_7 + c1_7)%2) + (2**13)*((c0_8 + c1_8)%2) + (2**14)*((c0_9 + c1_9)%2) + (2**15)*((c1_12 + c2_12)%2) + (2**16)*((c1_11 + c2_11)%2) + (2**17)*((c0_2 + c2_2)%2) + (2**18)*((c0_3 + c2_3)%2) + (2**19)*((c0_4 + c2_4)%2) + (2**20)*e1_7 + (2**21)*e1_8 + (2**22)*e1_9 + (2**23)*e0_0 + (2**24)*(e0_1) + (2**25)*(e0_2)


def phi3_2(slice3):
    """
        3 slices of 12,13,14
    """
    [a0_12, a0_13, a0_14, a1_15, a1_0, a1_1, a2_0, a2_1, a2_2, b0_13, b0_14, b0_15, b1_6, b1_7, b1_8, b2_8, b2_9, b2_10, c0_10, c0_11, c0_12, c1_2, c1_3, c1_4, c2_7, c2_8, c2_9, e0_7, e0_8, e0_9, e1_0, e1_1, e1_2] = slice3
    return a0_12 + 2*(a0_13) + 4*(a0_14) + 8*(a1_0 + a2_0) + 16*(a1_1 + a2_1) + 32*(b1_6) +64*(b1_7) + 128*((b1_8 + b2_8)%2) + 256*b2_10 + 512*(b0_13) + 1024*(b0_14) + 2048*(b0_15) + (2**12)*(c2_7) + (2**13)*(c2_8) + (2**14)*(c2_9) + (2**15)*(c0_12) + (2**16)*(c0_11) + (2**17)*(c1_2) + (2**18)*(c1_3) + (2**19)*(c1_4) + (2**20)*e0_7 + (2**21)*e0_8 + (2**22)*e0_9 + (2**23)*e1_0 + (2**24)*(e1_1) + (2**25)*(e1_2)


def merge12_3groups(A, ind, slices12groups, slices3groups2):
    """
    """
    values = []
    # sort1st by phi31 function
    slice12 = sorted(slices12groups, key=lambda x : phi12(x) )
    slice3 = sorted(slices3groups2, key=lambda x : phi3_2(x) )

    n = len(slice12)
    m = len(slice3)

    values = []

    prev_j = 0
    i = 0
    j = 0
    while i < n:
        a = phi12 ( slice12[i] )
        b = phi3_2 ( slice3[ prev_j ] )
        if a == b:
            j = prev_j
        elif a > b:
            prev_j += 1
            j = prev_j
        elif a < b:
            i+=1
        while j < m:
            if phi12 ( slice12[i] ) == phi3_2 ( slice3[j] ):
                [a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7,
                        c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6,
                        e0_11, e0_12, e0_13, e0_14, e0_15, e0_0,  e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e1_4, e1_5, e1_6, e1_7, e1_8, e1_9, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15] = slice12[i]
                [a0_12, a0_13, a0_14, a1_15, a1_0, a1_1, a2_0, a2_1, a2_2, b0_13, b0_14, b0_15, b1_6, b1_7, b1_8, b2_8, b2_9, b2_10, c0_10, c0_11, c0_12, c1_2, c1_3, c1_4, c2_7, c2_8, c2_9, e0_7, e0_8, e0_9, e1_0, e1_1, e1_2] = slice3[j]
                
                slice11 = [ [a0_11, b2_7, c2_1, 0, 0], [0, e1_15, a1_14, 0, 0], [b0_12, c1_1, 0, 0, 0], [e0_6, a2_15, b1_5, 0, 0], [c0_9, 0, 0, 0, 0]]
                slice12 = [ [a0_12, b2_8, c2_2, 0, 0], [0, e1_0, a1_15, 0, 0], [b0_13, c1_2, 0, 0, 0], [e0_7, a2_0, b1_6, 0, 0], [c0_10, 0, 0, 0, 0]]

                result = check( slice11, slice12, A, ind)
                # if output slice bits satisfied
                if result:
                    values.append([
                        a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a0_12, a0_13, a0_14, 
                        a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a1_15, a1_0, a1_1, 
                        a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, a2_0, a2_1, a2_2, 
                        b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b0_13, b0_14, b0_15, 
                        b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b1_6, b1_7, b1_8, 
                        b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7, b2_8, b2_9, b2_10, 
                        c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c0_10, c0_11, c0_12, 
                        c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c1_2, c1_3, c1_4, 
                        c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6, c2_7, c2_8, c2_9, 
                        e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e0_7, e0_8, e0_9, 
                        e1_4, e1_5, e1_6, e1_7, e1_8, e1_9, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15, e1_0, e1_1, e1_2
                        ])
                j+=1
            else:
                break
        i+=1
    return values


def get1slice(i,output):
    """
        Get last slice
    """
    values = []
    for a0_15, a1_2, a2_3, b0_0, b1_9, b2_11, c0_13, c1_5, c2_10, e0_10, e1_3 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
        values.append( [ a0_15, a1_2, a2_3, b0_0, b1_9, b2_11, c0_13, c1_5, c2_10, e0_10, e1_3 ] )
    output.put((i,values))


def phi15(slice15):
    """
    """
    [
        a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a0_12, a0_13, a0_14, 
        a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a1_15, a1_0, a1_1, 
        a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, a2_0, a2_1, a2_2, 
        b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b0_13, b0_14, b0_15, 
        b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b1_6, b1_7, b1_8, 
        b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7, b2_8, b2_9, b2_10, 
        c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c0_10, c0_11, c0_12, 
        c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c1_2, c1_3, c1_4, 
        c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6, c2_7, c2_8, c2_9, 
        e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e0_7, e0_8, e0_9, 
        e1_4, e1_5, e1_6, e1_7, e1_8, e1_9, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15, e1_0, e1_1, e1_2
    ] = slices15

    return (a1_15 + a2_15)%2 + 2*((a0_2 + a2_2) % 2) + 4*((a0_3 + a1_3)%2) + 8*((b1_0 + b2_0) % 2) + 16*((b0_9 + b2_9)%2) + 32*((b0_11 + b1_11)%2) + 64*((c1_13 + c2_13)%2) + 128*((c0_5 + c2_5)%2) + 256*((c0_10 + c1_10)%2) + 512*(e1_10) + 1024*(e0_3)


def phi1(slice1):
    """
    """
    [ a0_15, a1_2, a2_3, b0_0, b1_9, b2_11, c0_13, c1_5, c2_10, e0_10, e1_3 ] = slice1
    return a0_15 + 2*a1_2 + 4*a2_3 + 8*b0_0 + 16*b1_9 + 32*b2_11 + 64*c0_13 + 128*c1_5 + 256*c2_10 + 512*e0_10 + 1024*e1_3


def mergefinal(A, slices15groups, slice1rem):
    """
    """
    values = []
    # sort1st by phi31 function
    slice15group = sorted(slices15groups, key=lambda x : phi15(x) )
    slice1 = sorted(slice1rem, key=lambda x : phi1(x) )

    n = len(slice15group)
    m = len(slice1)

    values = []

    prev_j = 0
    i = 0
    j = 0
    while i < n:
        a = phi15( slice15group[i] )
        b = phi1( slice1[ prev_j ] )
        if a == b:
            j = prev_j
        elif a > b:
            prev_j += 1
            j = prev_j
        elif a < b:
            i+=1
        while j < m:
            if phi15(slice15group[i]) == phi1( slice1[j] ):
                [
                    a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a0_12, a0_13, a0_14, 
                    a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a1_15, a1_0, a1_1, 
                    a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, a2_0, a2_1, a2_2, 
                    b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b0_13, b0_14, b0_15, 
                    b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b1_6, b1_7, b1_8, 
                    b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7, b2_8, b2_9, b2_10, 
                    c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c0_10, c0_11, c0_12, 
                    c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c1_2, c1_3, c1_4, 
                    c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6, c2_7, c2_8, c2_9, 
                    e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e0_7, e0_8, e0_9, 
                    e1_4, e1_5, e1_6, e1_7, e1_8, e1_9, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15, e1_0, e1_1, e1_2
                ] = slice15group[i]

                [ a0_15, a1_2, a2_3, b0_0, b1_9, b2_11, c0_13, c1_5, c2_10, e0_10, e1_3 ] = slice1[j]

                slice14 = [ [a0_14, b2_10, c2_9, 0, 0], [0, e1_2, a1_1, 0, 0], [b0_15, c1_4, 0, 0, 0], [e0_9, a2_2, b1_8, 0, 0], [c0_12, 0, 0, 0, 0]]
                slice15 = [ [a0_15, b2_11, c2_10, 0, 0], [0, e1_3, a1_2, 0, 0], [b0_0, c1_5, 0, 0, 0], [e0_10, a2_3, b1_9, 0, 0], [c0_13, 0, 0, 0, 0]]

                result = check( slice14, slice15, A, 15)
                # if output slice bits satisfied
                if result:

                    slice0 = [ [a0_0, b2_12, c2_11, 0, 0], [0, e1_4, a1_3, 0, 0], [b0_1, c1_6, 0, 0, 0], [e0_11, a2_4, b1_10, 0, 0], [c0_14, 0, 0, 0, 0]]
                    result2 = check( slice15, slice0, A, 0)

                    if result2:
                        values.append([
                            a0_0, a0_1, a0_2, a0_3, a0_4, a0_5, a0_6, a0_7, a0_8, a0_9, a0_10, a0_11, a0_12, a0_13, a0_14, a0_15,
                            a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11, a1_12, a1_13, a1_14, a1_15, a1_0, a1_1, a1_2, 
                            a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11, a2_12, a2_13, a2_14, a2_15, a2_0, a2_1, a2_2, a2_3,
                            b0_1, b0_2, b0_3, b0_4, b0_5, b0_6, b0_7, b0_8, b0_9, b0_10, b0_11, b0_12, b0_13, b0_14, b0_15, b0_0,
                            b1_10, b1_11, b1_12, b1_13, b1_14, b1_15, b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b1_6, b1_7, b1_8, b1_9,
                            b2_12, b2_13, b2_14, b2_15, b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7, b2_8, b2_9, b2_10, b2_11,
                            c0_14, c0_15, c0_0, c0_1, c0_2, c0_3, c0_4, c0_5, c0_6, c0_7, c0_8, c0_9, c0_10, c0_11, c0_12, c0_13,
                            c1_6, c1_7, c1_8, c1_9, c1_10, c1_11, c1_12, c1_13, c1_14, c1_15, c1_0, c1_1, c1_2, c1_3, c1_4, c1_5,
                            c2_11, c2_12, c2_13, c2_14, c2_15, c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6, c2_7, c2_8, c2_9, c2_10,
                            e0_11, e0_12, e0_13, e0_14, e0_15, e0_0, e0_1, e0_2, e0_3, e0_4, e0_5, e0_6, e0_7, e0_8, e0_9, e0_10,
                            e1_4, e1_5, e1_6, e1_7, e1_8, e1_9, e1_10, e1_11, e1_12, e1_13, e1_14, e1_15, e1_0, e1_1, e1_2, e1_3
                            ])
                j+=1
            else:
                break
        i+=1
    return values


if __name__ == '__main__':
    # size of state
    state_size = 400

    w = state_size//25

    digest = "1acc220b9e2ea7208d4861ba"

    bdigest = getreversePrintformat(digest)

    # Got State 4, Fig 9
    print("===========================================================================================================")
    A = digestToState(bdigest, w)
    print("===============================================STATE 4 CREATED================================================")
    print("===========================================================================================================")

    # Step 1 : Iota inverse (we initially has 2 rounds, so round index for last round was 23)
    rc = 1
    A = iotainverse(A, rc, w)
    A = ChiInverse(A, w)
    A = piInverse(A, w)
    A = rhoInverse(A, w)

    print("===========================================================================================================")
    print("===============================================STATE 3 CREATED================================================")
    # Now A is State 3, Fig 9
    # print(A)
    # 8 groups of 3 slices
    slices3groups = [ [] , [] , [], [] ]
    slices3groupsQ = mp.Manager().Queue()
    # for i in range(0, 12, 3):
    #     print("=============================================== 3 SLICE GROUP ================================================", i)
    #     # slices3groups.append( slices3(A, i) )
    #     slices3groups[i//3] = slices3(A, i)
    processes = [mp.Process(target=slices3,args=(A,i,slices3groupsQ)) for i in range(0, 12, 3)]
    print("=============================================== 3 SLICE GROUP start ================================================")

    for p in processes:
        p.start()
    print("=============================================== 3 SLICE GROUP join ================================================")
   
    for p in processes:
        p.join()
    results = [slices3groupsQ.get() for p in processes]
    print("=============================================== 3 SLICE GROUP sort ================================================")

    results.sort(key=lambda k: k[0])
    slices3groups = [a[1] for a in results]
    
    slices6groups = [ [], [] ]
    slices6groupsQ = mp.Manager().Queue()
    # for i in range(0, 12, 6):
    #     slice3_0 = slices3groups[i//3]
    #     slice3_1 = slices3groups[i//3 + 1]
    #     # slices6groups.append( merge3slices(A, i, slice3_0, slice3_1) )
    #     slices6groups[i//6]  = merge3slices(A, i, slice3_0, slice3_1)
    print("=============================================== 6 SLICE GROUP ================================================")
    processes = [mp.Process(target=slices6,args=(A,i,slices3groups[i//3],slices3groups[i//3 + 1],slices6groupsQ)) for i in range(0, 12, 6)]
    for p in processes:
        p.start()
    print("=============================================== 6 SLICE GROUP join ================================================")
    for p in processes:
        p.join()
    results = [slices6groupsQ.get() for p in processes]
    results.sort(key=lambda k: k[0])
    slices6groups = [a[1] for a in results]

    # deallocate memory from slices3groups
    # del slices3groups # or
    slices3groups = None

    outputsQ = mp.Manager().Queue()

    slices12groups = []
    # for i in range(0, 12, 12):
    #     print("=============================================== 12 SLICE GROUP ================================================", i)
    #     slice6_0 = slices6groups[i//6]
    #     slice6_1 = slices6groups[i//6 + 1]
    #     slices12groups.append( merge6slices(A, i, slice6_0, slice6_1) )
    # slices6groups = None

    slices3groups2 = []
    # slices3groups2.append( slices3(A, 12) )
    # print("=============================================== LAST 3 SLICE GROUP ================================================")

    
    # print("=============================================== merge of 12, 3 SLICE GROUPs ================================================")
    # slice1rem = get1slice()    
    print("===========================================12 slice, 3 slice started================================================")
    processes = [mp.Process(target=slices12,args=(A,0,slices6groups[0],slices6groups[1],outputsQ)),mp.Process(target=slices3,args=(A,12,outputsQ))]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    results = [outputsQ.get() for p in processes]
    results.sort(key=lambda k: k[0])

    slices12groups.append(results[0][1])
    slices3groups2.append(results[1][1])
    
    slices15groups = slices15(A, 12, slices12groups, slices3groups2)

    print("=============================================== LAST 1 SLICE ================================================")
    print("=============================================== LAST merge To be done ================================================")
    print("wait.............")
    solutions = slices16(A, 0, slices15groups)

    print( solutions )
