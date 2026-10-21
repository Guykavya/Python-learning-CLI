n = int(input())

min_price = int(input())     # cheapest price seen so far
min_day = 1                  # the first day it was that cheap
best = 0
buy_day = 0
sell_day = 0

for day in range(2, n + 1):
    price = int(input())
    # Selling today, the best buy is the cheapest earlier day.
    profit = price - min_price
    if profit > best:            # strictly greater: keep the earliest sell day on ties
        best = profit
        buy_day = min_day
        sell_day = day
    if price < min_price:        # strictly smaller: keep the earliest cheapest day
        min_price = price
        min_day = day

print(f"profit {best}")
if best > 0:
    print(f"buy {buy_day} sell {sell_day}")
