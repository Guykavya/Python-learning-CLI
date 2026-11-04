n, m = map(int, input().split())
a = [int(x) for x in input().split()]
b = [int(x) for x in input().split()]

common = sorted(set(a) & set(b))
print(len(common))
print(*common)
