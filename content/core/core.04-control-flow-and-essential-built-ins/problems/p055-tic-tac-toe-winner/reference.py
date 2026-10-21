r1 = input()
r2 = input()
r3 = input()
b = r1 + r2 + r3
x = b.count("X")
o = b.count("O")

shape_ok = len(r1) == len(r2) == len(r3) == 3 and all(ch in "XO." for ch in b)
if not shape_ok or not (x == o or x == o + 1):
    print("Invalid board")
else:
    wins = ""
    for p in "XO":
        won = False
        for i in range(3):
            row = all(b[3 * i + c] == p for c in range(3))
            col = all(b[3 * r + i] == p for r in range(3))
            won = won or row or col
        diag1 = all(b[4 * k] == p for k in range(3))
        diag2 = all(b[2 + 2 * k] == p for k in range(3))
        if won or diag1 or diag2:
            wins += p
    if wins == "XO" or (wins == "X" and x != o + 1) or (wins == "O" and x != o):
        print("Invalid board")
    elif wins:
        print(f"{wins} wins")
    elif "." not in b:
        print("Draw")
    else:
        print("In progress")
