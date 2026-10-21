## Approach

Keep the robot's state in variables. A loop-and-a-half reads commands; `match` on the words
decides what each command does; an inner loop takes the steps one at a time so it can stop at
a wall.

## Code

```python
w, h = input().split()
w = int(w)
h = int(h)
x = 0
y = 0
facing = "north"
steps = 0
while True:
    line = input().strip()
    match line.split():
        case ["stop"]:
            break
        case []:
            continue
        case ["move", n] if n.isdigit() and int(n) >= 1:
            for _ in range(int(n)):
                match facing:
                    case "north":
                        nx, ny = x, y + 1
                    case "south":
                        nx, ny = x, y - 1
                    case "east":
                        nx, ny = x + 1, y
                    case _:
                        nx, ny = x - 1, y
                if not (0 <= nx < w and 0 <= ny < h):
                    print(f"Bumped into wall at ({x}, {y})")
                    break
                x, y = nx, ny
                steps += 1
        case ["right"] | ["left"] | ["turn", "around"]:
            turns = {"right": 1, "left": 3, "turn": 2}[line.split()[0]] if False else 0
            if line == "right":
                turns = 1
            elif line == "left":
                turns = 3
            else:
                turns = 2
            for _ in range(turns):
                match facing:
                    case "north":
                        facing = "east"
                    case "east":
                        facing = "south"
                    case "south":
                        facing = "west"
                    case "west":
                        facing = "north"
        case ["where"]:
            print(f"At ({x}, {y}) facing {facing}")
        case _:
            print(f"Unknown: {line}")
print(f"Final: ({x}, {y}) facing {facing}")
print(f"Steps: {steps}")
```

## Why turning left is three rights

Three quarter-turns to the right face the same way as one to the left. Reusing one `match`
for every turn means there is only one place where the order of directions is written.

## Why step one square at a time

To stop exactly at the wall and report where, the robot must check each step. Jumping N
squares at once would need a separate calculation of how far it can go.

## Why the guard on `move`

`case ["move", n] if n.isdigit() and int(n) >= 1:` accepts only real step counts. `move -2` or
`move x` fall through to the wildcard and are reported as unknown.
