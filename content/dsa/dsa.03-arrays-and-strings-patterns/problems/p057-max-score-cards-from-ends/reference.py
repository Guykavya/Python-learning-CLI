n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

total = sum(a)
keep = n - k            # the cards left behind form a block of this many consecutive cards

window = sum(a[:keep])  # keep = 0 gives an empty block with sum 0
smallest = window
for i in range(keep, n):
    window += a[i] - a[i - keep]
    if window < smallest:
        smallest = window

print(total - smallest)
