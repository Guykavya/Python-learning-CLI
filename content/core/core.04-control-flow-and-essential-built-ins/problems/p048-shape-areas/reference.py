import math

count = 0
total = 0.0
while True:
    words = input().split()
    if words == ["done"]:
        break
    area = None
    sizes = []
    match words:
        case []:
            continue
        case ["circle", r]:
            sizes = [float(r)]
            area = math.pi * sizes[0] ** 2
        case ["rect", w, h]:
            sizes = [float(w), float(h)]
            area = sizes[0] * sizes[1]
        case ["square", s]:
            sizes = [float(s)]
            area = sizes[0] ** 2
        case ["triangle", b, h]:
            sizes = [float(b), float(h)]
            area = sizes[0] * sizes[1] / 2
        case ["circle", *_]:
            print("Usage: circle R")
        case ["rect", *_]:
            print("Usage: rect W H")
        case ["square", *_]:
            print("Usage: square S")
        case ["triangle", *_]:
            print("Usage: triangle B H")
        case [word, *_]:
            print(f"Unknown shape: {word}")
    if area is not None:
        if min(sizes) <= 0:
            print("Sizes must be positive")
        else:
            print(f"{words[0]} area: {area:.2f}")
            count += 1
            total += area
print(f"Shapes: {count}")
print(f"Total area: {total:.2f}")
