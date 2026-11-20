import math
import sys

NAMES = ["log n", "n", "n log n", "n sqrt n", "n^2", "n^3", "2^n"]


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    out = []
    for i in range(t):
        n = int(data[1 + 2 * i])
        s = int(data[2 + 2 * i])
        budget = 10**7 * s
        costs = [
            math.log2(n),
            n,
            n * math.log2(n),
            n * math.sqrt(n),
            n * n,
            n**3,
            2**n if n <= 60 else math.inf,
        ]
        best = 0
        for k, c in enumerate(costs):
            if c <= budget:
                best = k
        out.append(NAMES[best])
    print("\n".join(out))


main()
