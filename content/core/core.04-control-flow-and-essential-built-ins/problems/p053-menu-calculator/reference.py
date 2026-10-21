MENU = """Menu:
1) add
2) subtract
3) multiply
4) divide
5) power
?) show this menu
q) quit"""

print(MENU)
count = 0
while True:
    choice = input().strip().lower()
    match choice:
        case "":
            continue
        case "q" | "quit":
            break
        case "?":
            print(MENU)
        case "1" | "2" | "3" | "4" | "5":
            a = float(input())
            b = float(input())
            if choice == "4" and b == 0:
                print("Cannot divide by zero")
                continue
            match choice:
                case "1":
                    result = a + b
                case "2":
                    result = a - b
                case "3":
                    result = a * b
                case "4":
                    result = a / b
                case "5":
                    result = a ** b
            print(f"Result: {result:.2f}")
            count += 1
        case _:
            print(f"Unknown choice: {choice}")
word = "calculation" if count == 1 else "calculations"
print(f"Done. {count} {word}.")
