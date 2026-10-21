# Trace match patterns

Predict **exactly** what this program prints. Do not run it. Lists print with square brackets
and quotes around strings, like `['a', 'b']`.

```python
for cmd in ["go north", "go", "take red key", "drop", "", "look around", "GO west"]:
    words = cmd.lower().split()
    match words:
        case []:
            print("empty")
        case ["go"]:
            print("go where?")
        case ["go", direction] if direction in ("north", "south"):
            print("going", direction)
        case ["go", other]:
            print("cannot go", other)
        case ["take", *things]:
            print("taking", len(things), "things:", things)
        case ["drop" | "throw"]:
            print("drop what?")
        case [verb, *_]:
            print("unknown verb", verb)

for value in [0, 7, "7", 2.5, None, (1, 2), 3]:
    match value:
        case 0 | None:
            print(repr(value), "-> nothing")
        case int(n) if n > 5:
            print(n, "-> big int")
        case str():
            print(repr(value), "-> text")
        case (a, b):
            print("pair", a, b)
        case _:
            print(repr(value), "-> other")
```

Write your answer in `answer.txt`, one printed line per line.
