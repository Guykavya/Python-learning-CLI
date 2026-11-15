n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

total = sum(a)
keep = n - k            # the cards left behind form a block of this many consecutive cards
# TODO: find the smallest sum of `keep` consecutive cards with a sliding window
print(0)
