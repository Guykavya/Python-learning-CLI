top = input().split()
bottom = input().split()
if len(top) != len(bottom):
    print("Lines have different word counts")
else:
    line1 = ""
    line2 = ""
    for a, b in zip(top, bottom):
        width = max(len(a), len(b))
        line1 += (f"{a:>{width}}" if a.isdigit() else f"{a:<{width}}") + "  "
        line2 += (f"{b:>{width}}" if b.isdigit() else f"{b:<{width}}") + "  "
    print(line1.rstrip())
    print(line2.rstrip())
