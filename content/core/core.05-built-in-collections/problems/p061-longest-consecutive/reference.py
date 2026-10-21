values = set(int(x) for x in input().split())
best_len, best_start = 0, None
for x in values:
    if x - 1 not in values:
        length = 1
        while x + length in values:
            length += 1
        if length > best_len or (length == best_len and x < best_start):
            best_len, best_start = length, x
print("Length:", best_len)
if best_len:
    print(f"Run: {best_start} to {best_start + best_len - 1}")
