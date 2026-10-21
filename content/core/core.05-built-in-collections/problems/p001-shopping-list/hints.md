## Hint 1

You do not know how many lines are coming. Which loop keeps going until a condition says stop?

## Hint 2

Start with `items = []`. Inside a `while True:` loop, read a line, `break` if it is `done`,
otherwise `items.append(line)`.

## Hint 3

After the loop, `print(f"Items: {len(items)}")`. Then
`for i, item in enumerate(items, start=1): print(f"{i}. {item}")`.
