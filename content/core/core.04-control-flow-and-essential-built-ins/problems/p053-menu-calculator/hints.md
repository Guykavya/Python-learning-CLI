## Hint 1

The program repeats an unknown number of times and leaves from the middle when the user types
`q`. Which loop shape is that?

## Hint 2

Store the menu in one string (a triple-quoted string keeps the line breaks) and print it in
two places. In the `match`, `case "1" | "2" | "3" | "4" | "5":` handles all operations; read
the two numbers there, then choose the operation with another `match` or an `if`/`elif`.

## Hint 3

Sketch:
```
print(MENU)
count = 0
while True:
    choice = input().strip().lower()
    match choice:
        case "": continue
        case "q" | "quit": break
        case "?": print(MENU)
        case "1" | "2" | "3" | "4" | "5": ...
        case _: print(f"Unknown choice: {choice}")
```
