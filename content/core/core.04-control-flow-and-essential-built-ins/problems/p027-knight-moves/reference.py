files = "abcdefgh"
square = input().strip().lower()
if len(square) != 2 or square[0] not in files or square[1] not in "12345678":
    print("invalid square")
else:
    start_f = files.index(square[0])
    start_r = int(square[1])
    line = ""
    count = 0
    for f in range(8):
        for r in range(1, 9):
            if abs(f - start_f) * abs(r - start_r) == 2:
                line += f"{files[f]}{r} "
                count += 1
    print(line.strip())
    print(f"Moves: {count}")
