n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

first = {0: 0}      # prefix value -> the first index where it appeared (P[0] = 0 at index 0)
best = 0
# TODO: running prefix sum; look up prefix - k; remember only the FIRST index of each prefix value
print(best)
