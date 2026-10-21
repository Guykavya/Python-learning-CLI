a = input().split()
b = input().split()
if not all(int(x) <= int(y) for x, y in zip(a, a[1:])):
    print("Line 1 is not sorted")
elif not all(int(x) <= int(y) for x, y in zip(b, b[1:])):
    print("Line 2 is not sorted")
else:
    i = 0
    j = 0
    out = ""
    while i < len(a) and j < len(b):
        if int(a[i]) <= int(b[j]):
            out += a[i] + " "
            i += 1
        else:
            out += b[j] + " "
            j += 1
    while i < len(a):
        out += a[i] + " "
        i += 1
    while j < len(b):
        out += b[j] + " "
        j += 1
    print(out.strip() if out else "(empty)")
    print(f"From line 1: {len(a)}, from line 2: {len(b)}")
