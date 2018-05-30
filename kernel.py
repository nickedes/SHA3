from main import *
from random import randint

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


def main():
    w = 64
    A = [[[0 for z in range(w)] for y in range(5)] for x in range(5)]
    start = []
    for x in range(5):
        for y in range(5):
            start.append((x, y, 0))

    for rtuple in start:
        init_x, _y, init_z = rtuple
        result = 0
        orig_state = []
        next_state = []

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
            if init_x == _x and init_z == _z and len(orig_state) % 2 == 0 and len(next_state) % 2 == 0:
                result = 1
                print("original state : ")
                print(orig_state)
                print("next state : ")
                print(next_state)
                print("kernel found")
                break
            while 1:
                print(new_pos)
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
            break


if __name__ == '__main__':
    main()
