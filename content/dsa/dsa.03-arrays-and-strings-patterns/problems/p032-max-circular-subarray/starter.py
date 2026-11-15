n = int(input())
a = [int(x) for x in input().split()]
# TODO: the best subarray either does not wrap (Kadane) or wraps (total minus the worst subarray)
best = a[0]
print(best)
