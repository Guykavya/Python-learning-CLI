n = int(input())
seen = set()
order = []
for _ in range(n):
    name = input().strip()
    if name not in seen:
        seen.add(name)
        order.append(name)
print("Unique:", len(order))
for name in order:
    print(name)
