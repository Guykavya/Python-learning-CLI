n = int(input())
prices = [int(x) for x in input().split()]

cheapest = prices[0]       # the lowest price on any day so far
best = 0                   # not trading at all earns 0
for p in prices[1:]:
    if p - cheapest > best:
        best = p - cheapest        # sell today, having bought on the cheapest earlier day
    if p < cheapest:
        cheapest = p
print(best)
