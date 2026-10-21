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
