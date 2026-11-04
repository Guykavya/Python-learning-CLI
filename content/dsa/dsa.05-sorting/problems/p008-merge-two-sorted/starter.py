n, m = map(int, input().split())
a = [int(x) for x in input().split()]
b = [int(x) for x in input().split()]
# TODO: merge with two pointers (no sorted / .sort)
print(" ".join(map(str, a + b)))
