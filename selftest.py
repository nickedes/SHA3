from chi_diff import applyrho
from kernel import getBitposAfterOneRhoPi as lol
from kernel import getOneBitPos
import main

# line = input().split(" ")
# w = 64
# print(lol(int(line[0]), int(line[1]), w))

w = 64
for x in range(5):
	for y in range(5):
		for z in range(w):
			o1 = applyrho(x,y,z)

			A = [[[0 for k in range(w)] for j in range(5)] for i in range(5)]
			A[x][y][z] = 1

			A = main.rho(A, w)
			o2 = getOneBitPos(A, w)[0]
			if o1 != o2:
				print(x,y,z)
				input()
