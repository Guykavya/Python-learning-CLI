n = int(input())
a = [int(x) for x in input().split()]
m = int(input())
b = [int(x) for x in input().split()]
# TODO: pointers i and j; take the smaller front each step; then copy what is left
out = a + b
print(*out)
