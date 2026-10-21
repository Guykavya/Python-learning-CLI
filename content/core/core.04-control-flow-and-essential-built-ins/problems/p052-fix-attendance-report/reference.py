# Attendance report (fixed).
names = input().split()
low = 0
for n, name in enumerate(names, start=1):
    marks = input().strip()
    present = 0
    for mark in marks:
        if mark in "Pp":
            present += 1
    days = len(marks)
    percent = present / days * 100
    line = f"{n}. {name}: {present}/{days} ({percent:.0f}%)"
    if percent < 75:
        line += " LOW"
        low += 1
    print(line)
if low == 0:
    print("All students at 75% or above")
else:
    print(f"Low attendance: {low}")
