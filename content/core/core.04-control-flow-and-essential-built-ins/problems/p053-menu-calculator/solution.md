## Approach

A loop-and-a-half around a `match` on the choice. The operation cases share one branch that
reads the numbers, then a second `match` picks the operation. The division-by-zero guard
comes before dividing.

## Code

```python
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
```

## Design notes

- **One place for the menu.** A constant means the two prints can never disagree.
- **Guard before acting.** The zero check comes before `a / b`, so the crash can never happen.
- **`continue` and `break` inside `match`** act on the `while` loop, because `match` is not a loop.
- **Count only successes.** `count += 1` sits after the print of a result, so declined
  divisions are not counted.

## Extending it

The full project adds input validation for the numbers (without crashing on `abc`), a history
of results, and more operations. Each new operation is one new `case`.
