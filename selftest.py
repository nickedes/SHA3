from kernel import getBitposAfterOneRhoPi as lol

line = input().split(" ")
w = 64
print(lol(int(line[0]), int(line[1]), w))
