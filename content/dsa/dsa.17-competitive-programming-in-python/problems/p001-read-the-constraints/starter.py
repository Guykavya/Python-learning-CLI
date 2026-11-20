import sys

NAMES = ["log n", "n", "n log n", "n sqrt n", "n^2", "n^3", "2^n"]


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    for i in range(t):
        n = int(data[1 + 2 * i])
        s = int(data[2 + 2 * i])
        budget = 10**7 * s
        # TODO: compute the seven costs, keep the slowest class that fits
        print(NAMES[1])


main()
