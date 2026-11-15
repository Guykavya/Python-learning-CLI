n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

seen = {}           # remainder of a prefix sum -> how many prefixes so far had it
total = 0
# TODO: remember the empty prefix; for each element update the remainder, add how many earlier prefixes share it
print(total)
