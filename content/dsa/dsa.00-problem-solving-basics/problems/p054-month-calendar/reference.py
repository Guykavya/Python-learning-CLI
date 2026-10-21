year = int(input())
month = int(input())

# Sub-problem 1: how many days does the month have?
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
if month == 2:
    if leap:
        length = 29
    else:
        length = 28
elif month == 4 or month == 6 or month == 9 or month == 11:
    length = 30
else:
    length = 31

# Sub-problem 2: which weekday is the 1st? (Zeller's congruence)
m = month
y = year
if m < 3:
    m += 12
    y -= 1
k = y % 100
j = y // 100
h = (1 + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
# Zeller gives 0 = Saturday, 1 = Sunday, 2 = Monday, ...; shift so that 0 = Monday.
first = (h + 5) % 7

# Sub-problem 3: print the grid, 7 cells per line.
print("Mo Tu We Th Fr Sa Su")
line = ""
col = 0
day = 1 - first          # days before the 1st are blank cells
while day <= length:
    if day < 1:
        cell = "  "
    else:
        cell = f"{day:>2}"
    if col > 0:
        line += " "
    line += cell
    col += 1
    if col == 7:
        print(line)
        line = ""
        col = 0
    day += 1
if col > 0:
    print(line)
