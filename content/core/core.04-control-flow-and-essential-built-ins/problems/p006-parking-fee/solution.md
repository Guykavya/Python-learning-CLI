## Approach

Flatten the rules: reject the unknown type, deal with 0 hours, compute the base fee for
the vehicle, then adjust for the weekend. Each rule appears once.

## Code

```python
vehicle = input().strip().lower()
hours = int(input())
day = input().strip().lower()

if vehicle not in ("bike", "car", "truck"):
    print("Unknown vehicle")
else:
    if hours == 0:
        fee = 0
    elif vehicle == "bike":
        fee = min(10 * hours, 50)
    elif vehicle == "car":
        fee = 40 if hours <= 2 else 40 + 25 * (hours - 2)
    else:
        fee = 100 * hours
    if day == "weekend" and hours > 0:
        fee = 0 if vehicle == "bike" else fee + 20
    print(f"Fee: {fee}")
```

## Why this shape

A fully nested version (vehicle, then day, then hours) repeats the weekend rule three times
and the zero rule three times. Handling special cases first keeps each rule in one place, so
a change to "weekend extra is now 30" is a one-line edit.

## Another way

Nest by vehicle first and handle the weekend inside each branch. It works, but test it with
0 hours at the weekend: it is easy to charge the extra 20 for a car that never parked.
