# setting 1
# init
k = Keccak(2)
k.setLane0(1, 0)
k.setLane0(1, 2)
k.setLane0(1, 4)
k.setLane0(0, 4)
k.setLane0(0, 3)
k.setLane0(2, 3)
k.setLane0(2, 4)

for i in range(5):
    k.setLane0(3, i)

for i in range(5):
    k.setLane0(4, i)

x = [k.S[0][1][j] + k.S[0][0][j] + 1 for j in range(64)]
k.setLane(0, 2, x)

k.setLane1(1, 1)
k.setLane1(1, 3)

x = [k.S[2][1][j] + k.S[2][0][j] for j in range(64)]
k.setLane(2, 2, x)

k.theta()
k.rho()
k.pi()
k.chi(1)

k.Vartheta(1)

##################################################################################
# setting 2
# init
k = Keccak(2)
k.setLane0(1, 0)
k.setLane0(1, 2)
k.setLane0(1, 4)
k.setLane0(0, 4)
# k.setLane0(0,3)
# k.setLane0(2,3)
k.setLane0(2, 4)

for i in range(5):
    k.setLane0(3, i)

for i in range(5):
    k.setLane0(4, i)

x = [k.S[0][2][j] + k.S[0][1][j] + k.S[0][0][j] + 1 for j in range(64)]
k.setLane(0, 3, x)

k.setLane1(1, 1)
k.setLane1(1, 3)

x = [k.S[2][2][j] + k.S[2][1][j] + k.S[2][0][j] for j in range(64)]
k.setLane(2, 3, x)

k.theta()
k.rho()
k.pi(1)
k.chi(1)

k.Vartheta(1)
