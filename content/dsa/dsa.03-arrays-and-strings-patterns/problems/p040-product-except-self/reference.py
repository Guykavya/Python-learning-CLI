MOD = 10**9 + 7

n = int(input())
a = [int(x) for x in input().split()]

ans = [1] * n
left = 1                       # product of a[0..i-1]
for i in range(n):
    ans[i] = left
    left = left * a[i] % MOD

right = 1                      # product of a[i+1..n-1]
for i in range(n - 1, -1, -1):
    ans[i] = ans[i] * right % MOD
    right = right * a[i] % MOD

print(" ".join(map(str, ans)))
