n = int(input())
a = [int(x) for x in input().split()]
# TODO: slow pointer w (next write position), fast pointer r (reads every element)
w = n
print(w)
print(*a[:w])
