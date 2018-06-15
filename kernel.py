from main import *
from random import randint


def getBitposAfterOneRhoPi(x, y, w):
    """
    """
    B = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    # as rho, pi are translation invariant
    B[x][y][0] = 1
    B = rho(B, w)
    B = pi(B, w)
    return getxy(getOneBitPos(B, w))[0]


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


def statePrint(A, w, statebitlist):
    """
        statebitlist - Is a list of tuples of x,y,z positions where 1 in state
    """
    alpha = ''
    for z in range(w):
        s = "z = " + str(z) + "\n"
        flag = 0
        for y in range(5):
            for x in range(5):
                if A[x][y][z] == 1:
                    flag = 1
                    if (x, y, z) not in statebitlist:
                        alpha = (x, y, z)
                s += str(A[x][y][z]) + " "
            s += "\n"
        # if flag:
        #     print(s)
    return alpha


def getOneBitPos(A, w):
    alpha = []
    for z in range(w):
        for y in range(5):
            for x in range(5):
                if A[x][y][z] == 1:
                    alpha.append((x, y, z))
    return alpha


def getxy(BitPositions):
    alpha = []
    for tupl in BitPositions:
        alpha.append(tupl[:2])
    return alpha


def satisfyCon(statebitlist, negativeList):
    """
        negativeList : Is a list of x,y positions
        statebitlist : list of tuples of x,y & z positions
    """
    xytuples = getxy(statebitlist)
    for xy in xytuples:
        if xy in negativeList:
            return False
    return True


def main():
    w = 64
    A = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    start = []

    # differential path requirements
    # input diff cant have these
    negative_init = [(2, 3), (2, 4), (3, 0), (3, 1), (3, 2),
                     (3, 3), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]

    negative_out = [(0, 0), (0, 1), (0, 2), (0, 3), (0,4), (1, 0)]

    for x in range(5):
        for y in range(5):
            if (x, y) not in negative_init:
                start.append((x, y, 0))

    for rtuple in start:
        init_x, _y, init_z = rtuple
        result = 0
        orig_state = []
        next_state = []
        print(orig_state)
        A[init_x][_y][init_z] = 1
        orig_state.append(statePrint(A, w, orig_state))
        for i in range(1000):
            if i % 2 == 0:
                A = rho(A, w)
                A = pi(A, w)
                new_pos = statePrint(A, w, next_state)
                next_state.append(new_pos)
            else:
                A = piInverse(A, w)
                A = rhoInverse(A, w)
                new_pos = statePrint(A, w, orig_state)
                orig_state.append(new_pos)
            try:
                _x, prev_y, _z = new_pos
            except Exception as e:
                break
            if init_x == _x and init_z == _z and len(orig_state) % 2 == 0 and len(next_state) % 2 == 0 and satisfyCon(orig_state, negative_init):
                result = 1
                print("original state :delta 1 ")
                print(orig_state)
                print("next state : delta 2 ")
                print(next_state)
                break
            while 1:
                # print(orig_state, next_state)
                # print(new_pos)
                print("Enter y: other than " + str(prev_y))
                _y = randint(0, 4)
                # _y = int(input())
                if prev_y != _y:
                    break
            A[_x][_y][_z] = 1
            if i % 2 == 0:
                next_state.append((_x, _y, _z))
            else:
                orig_state.append((_x, _y, _z))
            if i == 999:
                print("nothing found!")
        if result == 1:
            A = rho(A, w)
            A = pi(A, w)
            A = rho(A, w)
            A = pi(A, w)
            delta3 = getOneBitPos(A, w)
            if satisfyCon(delta3, negative_out):
                print("kernel found")
                print("delta 3 : ")
                print(delta3)
                break
            continue


if __name__ == '__main__':
    main()
