n = int(input())
members = set(int(x) for x in input().split())   # build once: O(n)
q = int(input())

for k in range(q):
    x = int(input())
    if x in members:                              # O(1) on average
        print("YES")
    else:
        print("NO")
