from main import *
import random
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
	print(filledlanes)
	totalLanes = 25
	A = [ 
			[ [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ], 
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ],
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ],
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ],
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ]
		]

	H = [ [int(x) for x in bdigest[i : i + w]] for i in range(0, len(bdigest) - 15, w) ]
	print(H)
	A[0][0] = H[0]
	A[1][0] = H[1]
	A[2][0] = H[2]
	A[3][0] = H[3]
	A[4][0] = H[4]
	A[0][1] = H[5]
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

	RC_bin = "{:016b}".format(int(RCi[i], 16))
	RC = [int(x) for x in RC_bin][::-1]
	for z in range(w):
		A_[0][0][z] = A[0][0][z] ^ RC[z]

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


def printSlice(State, Slicenum):
	"""
		Print the slice of the State
	"""
	Slice = [ [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
	for x in range(5):
		for y in range(5):
			Slice[x][y] = State[x][y][Slicenum]
	print("Slice of State : ", Slice)


def paritychecker( A, i, slicei):
	"""
		Checks and find the parity for previous slice based on the ith slice
	"""
	slicei = applyChi(slicei)
	#iota step mapping for first round
	if i == 0:
		slicei[0][0] = slicei[0][0] ^ 1

	# parity
	c = [0 for x in range(5)]
	for x in range(5):
		c[x] = (slicei[x][0] + slicei[x][1] + slicei[x][2] + slicei[x][3] + slicei[x][4])%2

	# prev slice parity
	d = [ 0, 0, 0, 0, 0, 0, 0]
	d[1] = A[0][0][i] ^ slicei[0][0] ^ c[4]
	d[2] = A[1][1][i] ^ slicei[1][1] ^ c[0]
	d[3] = A[2][2][i] ^ slicei[2][2] ^ c[1]
	d[4] = A[3][3][i] ^ slicei[3][3] ^ c[2]
	d[0] = A[4][4][i] ^ slicei[4][4] ^ c[3]

	if (d[4] == A[3][0][i] ^ slicei[3][0] ^ c[2]) and (d[0] == A[4][1][i] ^ slicei[4][1] ^ c[3]):
		phi1 = d[0] + 2*d[1] + 4*d[2] + 8*d[3] + 16*d[4]
		phi2 = c[0] + 2*c[1] + 4*c[2] + 8*c[3] + 16*c[4]
		d[5] = phi1
		d[6] = phi2
		return d
	return []



def slices3(A, ind):
	"""
	"""
	# values for slice2
	values2 = []
	for a0_2, a1_5, a2_6, b0_3, b1_12, b2_14, c0_0, c1_8, c2_13, e0_13, e1_6 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
		slice2 = [ [a0_2, b2_14, c2_13, 0, 0], [0, e1_6, a1_5, 0, 0], [b0_3, c1_8, 0, 0, 0], [e0_13, a2_6, b1_12, 0, 0], [c0_0, 0, 0, 0, 0]]
		i = ind + 2

		parity = paritychecker(A, i, slice2)
		if len(parity) == 7:
			values2.append([ parity, [a0_2, a1_5, a2_6, b0_3, b1_12, b2_14, c0_0, c1_8, c2_13, e0_13, e1_6] ])


	values1 = []
	for a0_1, a1_4, a2_5, b0_2, b1_11, b2_13, c0_15, c1_7, c2_12, e0_12, e1_5 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
		slice1 = [ [a0_1, b2_13, c2_12, 0, 0], [0, e1_5, a1_4, 0, 0], [b0_2, c1_7, 0, 0, 0], [e0_12, a2_5, b1_11, 0, 0], [c0_15, 0, 0, 0, 0]]
		i = ind + 1

		parity = paritychecker(A, i, slice1)
		if len(parity) == 7:
			values1.append([parity, [a0_1, a1_4, a2_5, b0_2, b1_11, b2_13, c0_15, c1_7, c2_12, e0_12, e1_5] ])
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

	flag = 1
	print("=============================================== Merging ================================================")

	kk = 0
	while flag == 1:
		i = prev_i
		j = prev_j
		while i + 1 < n:
			if values1[i][0][6] < values1[i + 1][0][6]:
				break
			i = i + 1
		next_i = i + 1
		while j + 1 < m:
			if values2[j][0][5] < values2[j + 1][0][5]:
				break
			j = j + 1
		next_j = j + 1

		if values1[prev_i][0][6] == values2[prev_j][0][5]:
			i = prev_i
			j = prev_j
			while i < next_i:
				while j < next_j:
					kk = kk + 1
					parity = [ values1[i][0][0], values1[i][0][1], values1[i][0][2], values1[i][0][3] , values1[i][0][4], values1[i][0][5] ]
					parity.append( values2[j][0][6] )
					values.append( [  parity, values1[i][1], values2[j][1] ])
					j += 1
				i += 1
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
	del values1
	del values2
	print("=============================================== Merging Done================================================")
	print("slice 3 solution",kk)
	print(values[0])
	return values


def slices6(A, ind, values1, values2):
	list3 = {}
	solution3 = []
	d0 = 0
	d1 = 0
	phi3 = 0
	for phi3 in range(0, 32):
		t = phi3
		c0 = t % 2
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
			# iota step will not affect slice 3 and slice 9
			iota = 0
			if ( c0 == a0 ^ a1 ^ a2 ^ a3 ^ ((a4 ^ 1)*a8) ^ ((a6 ^ 1)*a9) ^ ((a7 ^ 1)*a10) ^ d0 ^ iota ) and ( c1 == a4 ^ a5 ^ a6 ^ a7 ^ d1 ) and ( c4 == (a1 ^ 1)*a4 ^ (a2 ^ 1)*a5 ^ (a0 ^ 1)*d1 ^ (d0 ^ 1)*a6 ^ (a3 ^ 1)*a7 ):
				slice3 = [[a3, a7, a10, 0, 0], [d0, a6, a9, 0, 0], [a2, a5, 0, 0, 0], [a1, a4, a8, 0, 0], [a0, d1, 0, 0, 0]]
				parity = paritychecker( A, ind+3, slice3)
				if len(parity) > 0:
					phi2 = parity[5]
					slice3in = getslicebits(slice3)
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
			phi2 = x[0] + (32)*(slice4[0]) + (64)*(slice5[0])
			solution3.append([phi2, slice3, slice4, slice5, phi5])

	values2 = None
	solution3 = sorted(solution3, key =lambda x : x[0])

	list0 = {}
	solution0 = []
	d0 = 0
	d1 = 0
	chk = 0
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
			# add iota only for slice 0, not effect on slice 6
			iota = 0
			if ind == 0:
				iota = 1
			if ( c0 == a0 ^ a1 ^ a2 ^ a3 ^ ((a4 ^ 1)*a8) ^ ((a6 ^ 1)*a9) ^ ((a7 ^ 1)*a10) ^ d0 ^ iota ) and ( c1 == a4 ^ a5 ^ a6 ^ a7 ^ d1 ) and ( c4 == (a1 ^ 1)*a4 ^ (a2 ^ 1)*a5 ^ (a0 ^ 1)*d1 ^ (d0 ^ 1)*a6 ^ (a3 ^ 1)*a7 ):
				slice0 = [[a3, a7, a10, 0, 0], [d0, a6, a9, 0, 0], [a2, a5, 0, 0, 0], [a1, a4, a8, 0, 0], [a0, d1, 0, 0, 0]]
				parity = paritychecker( A, ind, slice0)
				if len(parity) == 7:
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
			phi15 = x[0]
			phi2 = val[0][6] + (32)*((slice0[2] + slice1[1])%2) + (64)*((slice1[2] + slice2[1])%2)
			solution0.append([phi15, slice0, slice1, slice2, phi2])
	values1 = None
	solution0 = sorted(solution0, key =lambda x : x[4])

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
	kk=0
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
					kk=kk+1
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
	del solution0
	del solution3
	print("slice 6 solutions ",kk)
	return values


def slices12(A, ind, values1, values2):
	"""
	"""
	# modify phi5
	for i in range(len(values1)):
		[ phi15, slice0, slice1, slice2, slice3, slice4, slice5, phi5 ] = values1[i]
		phi5 = values1[i][7] + (2**5)*((slice3[1] + slice2[2]) % 2) + (2**6)*((slice4[1] + slice3[2]) % 2) + (2**7)*((slice5[1] ^ slice4[2]) % 2) + (2**8)*(slice5[2]) + (2**9)*((slice2[4] + slice0[5]) % 2) + (2**10)*((slice0[3] ^ slice5[5]) % 2) + (2**11)*(slice1[3]) + (2**12)*(slice2[3]) + (2**13)*(slice3[3]) + (2**14)*(slice4[3]) + (2**15)*((slice0[6] + slice3[8]) % 2) + (2**16)*((slice1[6] + slice4[8]) % 2) + (2**17)*((slice2[6] + slice5[8]) % 2) + (2**18)*(slice3[6]) + (2**19)*(slice0[7]) + (2**20)*(slice0[10]) + (2**21)*(slice1[10]) + (2**22)*(slice2[10]) + (2**23)*(slice0[9]) + (2**24)*(slice1[9]) + (2**25)*(slice2[9]) + (2**26)*(slice3[9]) + (2**27)*(slice4[9])
		values1[i][7] = phi5
	for i in range(len(values2)):
		[ phi5, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] = values2[i]
		phi5 = values2[i][0] + (2**5)*(slice6[0]) + (2**6)*(slice7[0]) + (2**7)*(slice8[0]) + (2**8)*((slice9[0] + slice6[1]) % 2) + (2**9)*(slice11[3]) + (2**10)*(slice7[4]) + (2**11)*((slice8[4] + slice6[5]) % 2) + (2**12)*((slice9[4] + slice7[5]) % 2) + (2**13)*((slice10[4] + slice8[5]) % 2) + (2**14)*((slice11[4] + slice9[5]) % 2) + (2**15)*(slice8[7]) + (2**16)*(slice9[7]) + (2**17)*(slice10[7]) + (2**18)*((slice11[7] + slice6[8])%2) + (2**19)*((slice8[6] + slice11[8]) % 2) + (2**20)*(slice9[9]) + (2**21)*(slice10[9]) + (2**22)*(slice11[9]) + (2**23)*(slice6[10]) + (2**24)*(slice7[10]) + (2**25)*(slice8[10]) + (2**26)*(slice9[10]) + (2**27)*(slice10[10])
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
	kk=0
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
					[ phi15, slice0, slice1, slice2, slice3, slice4, slice5, phi5 ] = values1[i]
					[ phi5_, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] = values2[j]
					values.append( [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, phi11 ] )
					kk=kk+1
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
	del values1
	del values2
	print("slice 12 solution ",kk)
	return values


def slices15(A, ind, values1, values2):
	"""
		values1 - 0 to 11 slices
		values2 - 12 to 14
	"""
	d0 = 0
	d1 = 0
	list3 = {}
	solution3 = []

	phi11_s1 = set()
	phi11_s2 = set()

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
				parity = paritychecker( A, ind, slice12)
				if len(parity) > 0:
					phi11 = parity[5]
					slice12in = getslicebits(slice12)
					if phi3 not in list3:
						list3[phi3] = [ [phi11, slice12in] ]
					else:
						list3[phi3].append([phi11, slice12in])
	tr = len(values2)
	zz = 0
	for val in values2:
		phi12 = val[0][5]
		phi14 = val[0][6]
		phi3list = list3[phi12]
		slice13 = val[1]
		slice14 = val[2]
		for x in phi3list:
			slice12 = x[1]
			# check phi11 calculation
			phi11 = x[0] + (2**5)*slice12[0] + (2**6)*slice13[0] + (2**7)*slice14[0] + (2**8)*((slice12[2] + slice13[1]) % 2) + (2**9)*(slice13[2] ^ slice14[1]) + (2**10)*(slice12[4]) + (2**11)*(slice13[4])\
					+ (2**12)*(slice14[4] ^ slice12[5]) + (2**13)*slice14[5] + (2**14)*slice12[3] + (2**15)*slice13[3] + (2**16)*slice14[3] + (2**17)*slice12[8] + (2**18)*slice13[8]\
					+ (2**19)*(slice14[8]) + (2**20)*slice13[6] + (2**21)*slice14[6] + (2**22)*slice12[7] + (2**23)*slice13[7] + (2**24)*slice14[7] + (2**25)*slice12[9] + (2**26)*slice13[9]\
					+ (2**27)*(slice14[9]) + (2**28)*slice12[10] + (2**29)*slice13[10] + (2**30)*slice14[10]
			solution3.append([phi11, slice12, slice13, slice14, phi14])
			phi11_s2.add(phi11)
			zz = zz + 1
	values2 = sorted(solution3, key = lambda x : x[0])
	solution3 = None
	i = 0
	temp = len(values1)
	while i < temp:
		[phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, phi11] = values1[i]
		phi11 = values1[i][13] + (2**5)*(slice9[1] ^ slice8[2]) + (2**6)*(slice10[1] ^ slice9[2]) + (2**7)*(slice11[1] ^ slice10[2]) + (2**8)*(slice0[0]) + (2**9)*slice1[0] + (2**10)*(slice5[3] ^ slice10[5])\
				+ (2**11)*(slice6[3] ^ slice11[5]) + (2**12)*slice7[3] + (2**13)*(slice0[4] ^ slice9[3]) + (2**14)*(slice3[4] ^ slice1[5]) + (2**15)*(slice4[4] ^ slice2[5])\
				+ (2**16)*(slice5[4] ^ slice3[5]) + (2**17)*(slice9[6] ^ slice1[7]) + (2**18)*(slice10[6] ^ slice2[7]) + (2**19)*(slice11[6] ^ slice3[7]) + (2**20)*(slice0[8] ^ slice5[7])\
				+ (2**21)*(slice1[8] ^ slice6[7]) + (2**22)*(slice7[8] ^ slice4[6]) + (2**23)*(slice8[8] ^ slice5[6]) + (2**24)*(slice9[8] ^ slice6[6]) + (2**25)*(slice3[10]) + (2**26)*(slice4[10])\
				+ (2**27)*slice5[10] + (2**28)*slice5[9] + (2**29)*slice6[9] + (2**30)*(slice7[9])
		values1[i][13] = phi11
		phi11_s1.add(phi11)
		i = i + 1

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
	kk = 0
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
					kk=kk+1
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
	del values1
	del values2
	print("slice 15 solution ",kk)
	return values


def slices16(A, ind, values1):
	"""
	"""
	# values for slice2
	values2 = []
	for a0, a1, a2, b0, b1, b2, c0, c1, c2, e0, e1 in itertools.product(range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2),range(2)):
		slice2 = [ [a0, b2, c2, 0, 0], [0, e1, a1, 0, 0], [b0, c1, 0, 0, 0], [e0, a2, b1, 0, 0], [c0, 0, 0, 0, 0]]
		parity = paritychecker(A, ind + 15, slice2)
		if len(parity) == 7:
			phi14 = parity[5]
			phi15 = parity[6]
			phi14 = phi14 + (2**5)*a0 + (2**6)*a1 + (2**7)*a2 + (2**8)*b0 + (2**9)*b1 + (2**10)*b2 + (2**11)*c0 + (2**12)*c1 + (2**13)*c2 + (2**14)*e0 + (2**15)*e1
			values2.append([ phi14, phi15, [a0, a1, a2, b0, b1, b2, c0, c1, c2, e0, e1] ])
	for i in range(len(values1)):
		[ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, phi14 ] = values1[i]
		phi14 = values1[i][16] + (2**5)*(slice12[1] ^ slice11[2]) + (2**6)*(slice2[0] ^ slice14[2]) + (2**7)*(slice0[1] ^ slice3[0]) + (2**8)*(slice6[4] ^ slice4[5]) + (2**9)*(slice8[3] ^ slice13[5]) + (2**10)*(slice10[3] ^ slice1[4]) + (2**11)*(slice7[7] ^ slice2[8]) + (2**12)*(slice7[6] ^ slice10[8]) + (2**13)*(slice12[6] ^ slice4[7]) + (2**14)*(slice6[10]) + (2**15)*(slice8[9])
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
	print("n",n)
	print("m",m)

	flag = 1
	kk=0
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
					if values1[i][0]== values2[j][1]:
						values.append( [ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, slice15, phi14 ] )
						kk=kk+1
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
	del values1
	del values2
	print("slice 16 solutions ",kk)
	return values


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


if __name__ == '__main__':

	state_size = 400

	# lane size
	w = state_size//25

	while True:
		hexdigest = ""
		for i in range(24):
			hexdigest += "{:x}".format(random.randint(0, 15))
		input()
		bitdigest = getreversePrintformat(hexdigest)
		print(hexdigest)
		# state 4 of attack
		A = digestToState(bitdigest, w)
		rc = 1
		A = iotainverse(A, rc, w)
		A = ChiInverse(A, w)
		A = piInverse(A, w)
		A = rhoInverse(A, w)
		
		# Now A is State 3, Fig 9
		# 4 groups of 3 slices
		slices3groups = [ [] , [] , [], [] ]

		for i in range(0, 12, 3):
			print("=============================================== 3 SLICE GROUP ================================================", i)
			slices3groups[i//3] = slices3(A, i)
			print(len(slices3groups[i//3]))

		slices6groups = [ [], [] ]
		for i in range(0, 12, 6):
			print("=============================================== 6 SLICE GROUP ================================================", i)
			slice3_0 = slices3groups[i//3]
			slice3_1 = slices3groups[i//3 + 1]
			# slices6groups.append( merge3slices(A, i, slice3_0, slice3_1) )
			slices6groups[i//6]  = slices6(A, i, slice3_0, slice3_1)

		# deallocate memory from slices3groups
		del slices3groups

		slices12groups = []
		for i in range(0, 12, 12):
			print("=============================================== 12 SLICE GROUP ================================================", i)
			slice6_0 = slices6groups[i//6]
			slice6_1 = slices6groups[i//6 + 1]

		slices12groups = slices12(A, i, slice6_0, slice6_1)
		
		del slices6groups
		slices3groups2 = slices3(A, 12)
		print("=============================================== LAST 3 SLICE GROUP ================================================")

		slices15groups = slices15(A, 12, slices12groups, slices3groups2)
		del slices3groups2
		print("=============================================== merge of 12, 3 SLICE GROUPs ================================================")
		print("=============================================== LAST merge To be done ================================================")
		print("wait.............")
		solutions = slices16(A, 0, slices15groups)
		del slices15groups
		print(solutions)
		for solution in solutions:
			[ phi15, slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, slice15, phi14 ] = solution
			# construct state from slices
			Slices = [slice0, slice1, slice2, slice3, slice4, slice5, slice6, slice7, slice8, slice9, slice10, slice11, slice12, slice13, slice14, slice15]
			w = len(Slices)
			for index, slicebits in enumerate(Slices):
				Slices[index] = getSlicefrombits(slicebits)
			Obtained_initialState = Construct_State(Slices)
			msg = getString(Obtained_initialState, w)
			print("msg : " , msg)

