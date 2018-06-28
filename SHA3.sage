class Keccak:

    RC = [0x0000000000000001,
          0x0000000000008082,
          0x800000000000808A,
          0x8000000080008000,
          0x000000000000808B,
          0x0000000080000001,
          0x8000000080008081,
          0x8000000000008009,
          0x000000000000008A,
          0x0000000000000088,
          0x0000000080008009,
          0x000000008000000A,
          0x000000008000808B,
          0x800000000000008B,
          0x8000000000008089,
          0x8000000000008003,
          0x8000000000008002,
          0x8000000000000080,
          0x000000000000800A,
          0x800000008000000A,
          0x8000000080008081,
          0x8000000000008080,
          0x0000000080000001,
          0x8000000080008008]

    # Rotation offsets
    r = [[0,  36,   3,  41,  18],
         [1,  44,  10,  45,   2],
         [62,  6,  43,  15,  61],
         [28, 55,  25,  21,  56],
         [27, 20,  39,   8,  14]]

    def __init__(self, mode=0, values=[]):
        self.createBR()
        if mode == 0:
            self.createEmptyState()
        if mode == 1:
            self.createState(values)
        if mode == 2:
            self.createVariableState()

    def clear():
        print
        print
        print
        print
        print
        print

    def createBR(self):
        self.R = PolynomialRing(
            GF(2), ['a%d_%d' % (i, j) for i in range(28) for j in [0] + range(63, 0, -1)])
        self.R.inject_variables(scope=None, verbose=False)

    def createEmptyState(self):
        self.S = [[[list(GF(2))[0] for k in xrange(64)]
                   for j in xrange(5)] for i in xrange(5)]

    def createState(self, values=[]):
        if len(values) < 5*5*64:
            values = values + [0 for i in range(5*5*64 - len(values))]
        self.createEmptyState()
        for j in range(5):
            for i in range(5):
                for k in range(64):
                    self.S[i][j][k] = values[k + (i * 64) + (j * 64 * 5)]

    def createVariableState(self):
        self.createState(list(self.R.gens()))
        self.variables = self.R.gens()
        self.Lvariables = []
        for i in xrange(25):
            self.Lvariables.append(list(self.variables[i*64:(i+1)*64]))

    def printState(self, k=1, latex=0):
        rows = []
        for j in range(4, -1, -1):
            new = []
            for i in range(5):
                new.append(str(self.S[i][j][k-1]))
            rows.append(new)
        if latex:
            pretty_print(table(rows=rows, frame=True))
        else:
            print(table(rows=rows, frame=True))

    def setLane0(self, i, j):
        self.S[i][j] = [list(GF(2))[0] for k in xrange(64)]

    def setLane1(self, i, j):
        self.S[i][j] = [list(GF(2))[1] for k in xrange(64)]
 
    def setLane(self, i, j, value=[list(GF(2))[0] for i in xrange(64)]):
        self.S[i][j] = value

    def f(self, sround=1, eround=1, Print=0):
        while sround <= eround:
            self.theta(Print)
            self.rho(Print)
            self.pi(Print)
            self.chi(Print)
            self.iota(round=sround, Print=Print)
            sround = sround + 1

    def theta(self, Print=0):
        P = [[list(GF(2))[0] for k in range(64)] for i in range(5)]
        for i in xrange(5):
            for k in xrange(64):
                for j in xrange(5):
                    P[i][k] = P[i][k] + self.S[i][j][k]

        SS = [[[list(GF(2))[0] for k in xrange(64)]
               for j in xrange(5)] for i in xrange(5)]
        for i in range(5):
            for j in range(5):
                for k in range(64):
                    SS[i][j][k] = P[(i-1) % 5][k] + \
                        self.S[i][j][k] + P[(i+1) % 5][(k-1) % 64]
        self.S = SS
        if Print:
            self.printState()

    def rotate(self, L, r):
        return L[64-r:] + L[:64-r]

    def rho(self, Print=0):
        SS = [[[list(GF(2))[0] for k in xrange(64)]
               for j in xrange(5)] for i in xrange(5)]
        for i in range(5):
            for j in range(5):
                SS[i][j] = self.rotate(self.S[i][j], self.r[i][j])
        self.S = SS
        if Print:
            self.printState()

    def pi(self, Print=0):
        SS = [[[list(GF(2))[0] for k in xrange(64)]
               for j in xrange(5)] for i in xrange(5)]
        for i in range(5):
            for j in range(5):
                SS[j][(2*i + 3*j) % 5] = self.S[i][j]
        self.S = SS
        if Print:
            self.printState()

    def chi(self, Print=0):
        SS = [[[list(GF(2))[0] for k in xrange(64)]
               for j in xrange(5)] for i in xrange(5)]
        for i in range(5):
            for j in range(5):
                for k in range(64):
                    SS[i][j][k] = self.S[i][j][k] + \
                        (list(GF(2))[1] + self.S[(i+1) %
                                                 5][j][k])*self.S[(i+2) % 5][j][k]
        self.S = SS
        if Print:
            self.printState()

    def iota(self, round, Print=0):
        rc = int(str(self.RC[round-1]), 16)
        rc = [int(x) for x in list('{0:064b}'.format(rc))]
        for k in range(64):
            self.S[0][0][k] = self.S[0][0][k] + rc[k]
        if Print:
            self.printState()

    def Vartheta(self, Print=0):
        P = [[list(GF(2))[0] for k in range(64)] for i in range(5)]
        used_i = 25
        for i in xrange(used_i, used_i + 3):
            P[i-used_i] = list(self.variables[i*64:(i+1)*64])
            P[i-used_i] = P[i-used_i][:1]+ P[i-used_i][1:][::-1]

        for i in xrange(3, 5, 1):
            for k in xrange(64):
                for j in xrange(5):
                    P[i][k] = P[i][k] + self.S[i][j][k]

        SS = [[[list(GF(2))[0] for k in xrange(64)]
               for j in xrange(5)] for i in xrange(5)]
        for i in range(5):
            for j in range(5):
                for k in range(64):
                    SS[i][j][k] = P[(i-1) % 5][k] + \
                        self.S[i][j][k] + P[(i+1) % 5][(k-1) % 64]
        self.S = SS
        if Print:
            self.printState()
