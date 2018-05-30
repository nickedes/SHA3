from main import *


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


def statePrint(A, w):
    for z in range(w):
        s = "z = " + str(z) + "\n"
        flag = 0
        for y in range(5):
            for x in range(5):
                if A[x][y][z] == 1:
                    flag = 1
                s += str(A[x][y][z]) + " "
            s += "\n"
        if flag:
            print(s)


def main():
    w = 64
    A = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]

    start = []
    for x in range(5):
        for y in range(5):
            start.append((x,y))

    _x, _y = 3,1

    orig_state = [(_x, _y)]

    next_state = []

    A[_x][_y][0] = 1
    statePrint(A, w)
    for i in range(5):
        if i % 2 == 0:
            A = rho(A, w)
            A = pi(A, w)
            next_state.append((_x, _y))
        else:
            A = piInverse(A, w)
            A = rhoInverse(A, w)
            orig_state.append((_x, _y))
        statePrint(A, w)
        print("Enter x, y, z :")
        line = input()
        _x, _y, _z = [int(j) for j in line.split(" ")]
        A[_x][_y][_z] = 1



if __name__ == '__main__':
    main()
