old = {}
for pair in input().split():
    name, price = pair.split("=")
    old[name] = int(price)
new = {}
for pair in input().split():
    name, price = pair.split("=")
    new[name] = int(price)
merged = old | new
for item in sorted(merged):
    print(f"{item}: {merged[item]}")
changed = sorted(item for item in new if item in old and old[item] != new[item])
print("Changed:", ", ".join(changed) if changed else "none")
