# setting 1
# init
k1 = Keccak(2)
k1.setLane0(1, 0)
k1.setLane0(1, 2)
k1.setLane0(1, 4)
k1.setLane0(0, 4)
k1.setLane0(0, 3)
k1.setLane0(2, 3)
k1.setLane0(2, 4)

for i in range(5):
    k1.setLane0(3, i)

for i in range(5):
    k1.setLane0(4, i)

x = [k1.S[0][1][j] + k1.S[0][0][j] + 1 for j in range(64)]
k1.setLane(0, 2, x)

k1.setLane1(1, 1)
k1.setLane1(1, 3)

x = [k1.S[2][1][j] + k1.S[2][0][j] for j in range(64)]
k1.setLane(2, 2, x)

k1.theta(1)
k1.rho(1)
k1.pi(1)
k1.chi(1)

# k.Vartheta(1)

# setting 2
# init
k = Keccak(2)
k.setLane0(1, 0)
k.setLane0(1, 2)
k.setLane0(1, 4)
k.setLane0(0, 4)
# k.setLane0(0, 3)
k.setLane0(2, 3)
k.setLane0(2, 4)

for i in range(5):
    k.setLane0(3, i)

for i in range(5):
    k.setLane0(4, i)

x = [k.S[0][2][j] + k.S[0][1][j] + k.S[0][0][j] + 1 for j in range(64)]
k.setLane(0, 3, x)

k.setLane1(1, 1)
k.setLane1(1, 3)

x = [k.S[2][1][j] + k.S[2][0][j] for j in range(64)]
k.setLane(2, 2, x)

k.theta(1)
k.rho(1)
k.pi(1)
k.chi(1)

# k.Vartheta(1)

# SETTING 3!!!!!!!
# 


state = Keccak(2)
state.setLane0(0,4)
state.setLane0(1,4)
state.setLane0(2,4)
state.setLane0(3,4)
state.setLane0(4,4)
state.setLane0(2,3)
state.setLane0(3,3)
state.setLane0(4,3)

for x in [1,2,3,4]:
	for y in [0,1,2,3,4]:
		state.setLane0(x,y)

for y in [1,2,3,4]:
		state.setLane0(0,y)

