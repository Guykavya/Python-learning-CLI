n = int(input())
for _ in range(n):
    text = input().strip().upper()
    if not text or not all(ch in "IVXLCDM" for ch in text):
        print(f"{text} is not a Roman numeral")
        continue
    total = 0
    for ch, nxt in zip(text, text[1:] + " "):
        values = []
        for symbol in (ch, nxt):
            match symbol:
                case "I":
                    v = 1
                case "V":
                    v = 5
                case "X":
                    v = 10
                case "L":
                    v = 50
                case "C":
                    v = 100
                case "D":
                    v = 500
                case "M":
                    v = 1000
                case _:
                    v = 0
            values += [v]
        if values[0] < values[1]:
            total -= values[0]
        else:
            total += values[0]
    print(f"{text} = {total}")
