n = int(input())
a = [int(x) for x in input().split()]

m = sum(a)              # number of ones = size of the final block
# TODO: slide a window of size m around the circle (index i % n) and keep the most ones seen in it
print(m)
