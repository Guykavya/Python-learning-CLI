n = int(input())

prev = int(input())
cur_start = 1        # where the current streak began
cur_len = 1
best_start = 1
best_len = 1

for pos in range(2, n + 1):
    x = int(input())
    if x > prev:
        cur_len += 1
    else:
        cur_start = pos      # the streak is broken; a new one starts here
        cur_len = 1
    # Check after every number, so a streak that ends at the last position is counted.
    if cur_len > best_len:   # strictly greater: keep the earliest on ties
        best_len = cur_len
        best_start = cur_start
    prev = x

print(f"length {best_len}")
print(f"from {best_start} to {best_start + best_len - 1}")
