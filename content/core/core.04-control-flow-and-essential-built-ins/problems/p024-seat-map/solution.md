## Approach

For every row, walk along the seat letters and build the row's text. Count free seats and
all seats as you go.

## Code

```python
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
```

## Why nonexistent bookings need no code

We only ever ask "is this real seat booked?". A booking for `9Z` is never asked about, so it
is ignored automatically. Asking from the seat's side, not the booking's side, avoids a whole
class of bugs.

## Another way

Count the seats per row once (`len(letters.replace(" ", ""))`) and multiply by the rows for
the total.
