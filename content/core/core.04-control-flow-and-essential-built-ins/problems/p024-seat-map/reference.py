rows = int(input())
letters = input()
booked = input().split()
free = 0
total = 0
for row in range(1, rows + 1):
    line = f"Row {row:>2}: "
    for letter in letters:
        if letter == " ":
            line += " "
            continue
        total += 1
        if f"{row}{letter}" in booked:
            line += "X"
        else:
            line += letter
            free += 1
    print(line)
print(f"Free: {free} of {total}")
