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
        if flag:
            print(s)
    return alpha


def main():
    w = 64
    A = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]

    start = []
    for x in range(5):
        for y in range(5):
            start.append((x, y))

    _x, _y, _z = 3, 1, 0

    orig_state = []
    next_state = []

    A[_x][_y][_z] = 1
    orig_state.append(statePrint(A, w, orig_state))
    for i in range(5):
        if i % 2 == 0:
            A = rho(A, w)
            A = pi(A, w)
            new_pos = statePrint(A, w, next_state)
            if new_pos == '':
                print("done")
            else:
                next_state.append(new_pos)
            print(next_state)
        else:
            A = piInverse(A, w)
            A = rhoInverse(A, w)
            new_pos = statePrint(A, w, orig_state)
            if new_pos == '':
                print("done")
            else:
                orig_state.append(new_pos)
            print(orig_state)
        print("Enter x, y, z :")
        line = input()
        _x, _y, _z = [int(j) for j in line.split(" ")]
        A[_x][_y][_z] = 1


if __name__ == '__main__':
    main()
