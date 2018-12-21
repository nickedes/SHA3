from main import *
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

	totalLanes = 25
	A = [ 
			[ [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ], 
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ],
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ],
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ],
			[ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] ]
		]

	H = [ [int(x) for x in bdigest[i : i + w]] for i in range(0, len(bdigest) - 15, w) ]
	
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

	if d[4] == A[3][0][i] ^ slicei[3][0] ^ c[2] and d[0] == A[4][1][i] ^ slicei[4][1] ^ c[3]:
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

	kk=0
	while flag == 1:
		i = prev_i
		j = prev_j
		while i + 1 < n:
			if values1[i][0][6] < values1[i + 1][0][6]:
				break
			i= i + 1
		next_i = i + 1
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
					kk = kk + 1
					parity = [ values1[i][0][0], values1[i][0][1], values1[i][0][2], values1[i][0][3] , values1[i][0][4], values1[i][0][5] ]
					parity.append( values2[j][0][6] )
					values.append( [  parity, values1[i][1], values2[j][1] ])
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
	print("slice 3 solution",kk)
	return values


if __name__ == '__main__':

	state_size = 400

	# lane size
	w = state_size//25

	hexdigest = "100000000000000000000000"

	bitdigest = getreversePrintformat(hexdigest)
	# state 4 of attack
	A = digestToState(bitdigest, w)
	rc = 19
	A = iotainverse(A, rc, w)
	A = ChiInverse(A, w)
	A = piInverse(A, w)
	A = rhoInverse(A, w)
	
	# Now A is State 3, Fig 9
	# 4 groups of 3 slices
	slices3groups = [ [] , [] , [], [] ]

	for i in range(0, 12, 3):
		slices3groups[i//3] = slices3(A, i)
		print(len(slices3groups[i//3]))
