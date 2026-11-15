n = int(input())
A = [int(x) for x in input().split()]
B = [int(x) for x in input().split()]
C = [int(x) for x in input().split()]
D = [int(x) for x in input().split()]

pair_count = {}
for a in A:
    for b in B:
        s = a + b
        pair_count[s] = pair_count.get(s, 0) + 1

answer = 0
for c in C:
    for d in D:
        answer += pair_count.get(-(c + d), 0)
print(answer)
