n = int(input())
count = 0
line = ""
for x in range(2, n + 1):
    if x % 2 == 0 and x != 2:
        continue  # even numbers above 2 are never prime
    is_prime = True
    d = 3
    while d * d <= x:
        if x % d == 0:
            is_prime = False
            break
        d += 2
    if is_prime:
        count += 1
        if line == "":
            line = f"{x}"
        else:
            line = line + " " + f"{x}"
if count > 0:
    print(line)
print(f"count {count}")
