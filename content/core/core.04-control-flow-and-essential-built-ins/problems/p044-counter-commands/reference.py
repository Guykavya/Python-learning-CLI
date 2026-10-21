counter = 0
while True:
    line = input().strip()
    match line.split():
        case []:
            continue
        case ["quit"]:
            break
        case ["add", n]:
            counter += int(n)
        case ["sub", n]:
            counter -= int(n)
        case ["add" | "sub"]:
            print("Missing number")
        case ["double"]:
            counter *= 2
        case ["reset"]:
            counter = 0
        case ["show"]:
            print(f"Counter: {counter}")
        case _:
            print(f"Unknown command: {line}")
print(f"Final: {counter}")
