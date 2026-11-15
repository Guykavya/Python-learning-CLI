n, k = map(int, input().split())
a = [int(x) for x in input().split()]
# TODO: count values, sort distinct values by (-count, value), print the first k
print(*a[:k])
