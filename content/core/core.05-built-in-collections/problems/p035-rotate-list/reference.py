items = input().split()
k = int(input())
n = len(items)
if n == 0:
    print("(empty)")
else:
    k %= n
    print(" ".join(items[n - k:] + items[:n - k]))
