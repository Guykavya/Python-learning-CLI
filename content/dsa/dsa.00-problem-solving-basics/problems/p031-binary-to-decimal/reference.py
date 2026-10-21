s = input()

value = 0
valid = True
for ch in s:
    if ch == "0":
        value = value * 2
    elif ch == "1":
        value = value * 2 + 1
    else:
        valid = False
        break

if valid:
    print(value)
else:
    print("invalid")
