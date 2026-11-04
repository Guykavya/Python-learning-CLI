B = 131
M = 1_000_000_007

s = input().strip()
q = int(input())
# TODO: prefix hashes P and powers of B; answer each query in O(1)
for _ in range(q):
    l, r = map(int, input().split())
    print(0)
