mark = int(input())
if mark < 0 or mark > 100:
    print("invalid")
elif mark >= 90:
    print("A")
elif mark >= 75:
    print("B")
elif mark >= 60:
    print("C")
elif mark >= 40:
    print("D")
else:
    print("F")
