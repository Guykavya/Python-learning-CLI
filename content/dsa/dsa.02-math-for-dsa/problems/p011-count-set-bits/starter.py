import sys

data = sys.stdin.read().split()
q = int(data[0])
for token in data[1:1 + q]:
    n = int(token)
    # TODO: repeat n = n & (n - 1) until n is 0, and count the rounds
    print(0)
