MOD = 10**9 + 7
n = int(input())
a = [int(x) for x in input().split()]
# TODO: answer[i] = (product of everything left of i) * (product of everything right of i), modulo MOD
print(" ".join(["1"] * n))
