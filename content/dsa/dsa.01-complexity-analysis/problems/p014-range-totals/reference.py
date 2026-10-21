n = int(input())
a = [int(x) for x in input().split()]
q = int(input())

# before[k] = a[0] + ... + a[k - 1], the total of the first k days. before[0] = 0.
before = [0] * (n + 1)
for k in range(n):
    before[k + 1] = before[k] + a[k]

for k in range(q):
    l, r = [int(x) for x in input().split()]
    print(before[r] - before[l - 1])
