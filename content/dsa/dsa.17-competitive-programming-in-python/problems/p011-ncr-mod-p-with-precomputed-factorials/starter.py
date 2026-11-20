import sys

P = 10**9 + 7
data = sys.stdin.read().split()
q = int(data[0])
# TODO: precompute fact and inv_fact up to the largest n, then answer each query
print("\n".join("0" for _ in range(q)))
