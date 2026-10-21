colours = {}
for _ in range(int(input())):
    key, value = input().split()
    colours[key] = value
inverted = {v: k for k, v in colours.items()}
for v, k in inverted.items():
    print(f"{v} -> {k}")
