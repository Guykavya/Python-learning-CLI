temps = input().split()
if len(temps) < 2:
    print("Not enough data")
else:
    best = 0
    best_day = 0
    for day, (before, after) in enumerate(zip(temps, temps[1:]), start=2):
        change = int(after) - int(before)
        shown = f"{change:+d}" if change else "0"
        print(f"Day {day}: {shown}")
        if change > best:
            best = change
            best_day = day
    if best > 0:
        print(f"Biggest rise: +{best} on day {best_day}")
    else:
        print("No rises")
