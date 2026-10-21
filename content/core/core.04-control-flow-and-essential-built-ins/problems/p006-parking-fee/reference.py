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
