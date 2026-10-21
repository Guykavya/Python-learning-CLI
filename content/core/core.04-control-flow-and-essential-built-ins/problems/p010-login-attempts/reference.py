pin = input().strip()
for left in range(2, -1, -1):
    if input().strip() == pin:
        print("Welcome")
        break
    if left > 0:
        word = "try" if left == 1 else "tries"
        print(f"Wrong PIN. {left} {word} left")
    else:
        print("Wrong PIN. Card blocked")
