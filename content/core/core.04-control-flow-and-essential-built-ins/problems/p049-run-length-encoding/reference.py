text = input()
if not text:
    print("(empty)")
else:
    result = ""
    current = text[0]
    count = 0
    for ch in text:
        if ch == current:
            count += 1
        else:
            result += f"{current}{count}"
            current = ch
            count = 1
    result += f"{current}{count}"
    print(result)
