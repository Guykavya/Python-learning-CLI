n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
for _ in range(q):
    l, r = map(int, input().split())
    # TODO: i = l - 1, j = r - 1; swap and move inwards while i < j
print(*a)
