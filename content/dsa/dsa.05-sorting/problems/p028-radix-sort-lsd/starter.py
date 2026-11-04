n = int(input())
a = [int(x) for x in input().split()]
# TODO: LSD radix sort: one stable bucket pass per digit, ones digit first
print(" ".join(map(str, a)))
