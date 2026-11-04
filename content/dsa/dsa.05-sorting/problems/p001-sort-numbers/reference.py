n = int(input())
a = [int(x) for x in input().split()]
print(" ".join(map(str, sorted(a))))
print(" ".join(map(str, sorted(a, reverse=True))))
