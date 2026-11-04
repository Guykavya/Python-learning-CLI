n = int(input())
prices = [int(x) for x in input().split()]
# TODO: walk once; remember the cheapest price so far and the best profit of selling today
print(max(prices) - min(prices))
