# Attendance report (buggy). Fix it so it matches the specification.
names = input().split()
low = 0
for i in range(1, len(names)):
    marks = input().strip()
    present = 0
    for mark in marks:
        if mark == "P" or "p":
            present += 1
    days = len(marks)
    percent = present // days * 100
    line = f"{i}. {names[i]}: {present}/{days} ({percent:.0f}%)"
    if percent <= 75:
        line += " LOW"
        low += 1
    print(line)
else:
    print("All students at 75% or above")
if low:
    print(f"Low attendance: {low}")
