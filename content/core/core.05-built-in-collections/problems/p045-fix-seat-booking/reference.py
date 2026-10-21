# Cinema seat booking (fixed).
rows, cols = [int(x) for x in input().split()]
seats = [["."] * cols for _ in range(rows)]
snapshot = [row[:] for row in seats]
history = []
while True:
    parts = input().split()
    if parts[0] == "done":
        break
    if parts[0] == "book":
        r, c = int(parts[1]), int(parts[2])
        if seats[r][c] == ".":
            seats[r][c] = "X"
            history.append((r, c))
            print("Booked", r, c)
        else:
            print("Seat", r, c, "is taken")
    elif parts[0] == "undo":
        if history:
            r, c = history.pop()
            seats[r][c] = "."
            print("Undid", r, c)
        else:
            print("Nothing to undo")
    elif parts[0] == "save":
        snapshot = [row[:] for row in seats]
        print("Saved")
print("Seats:")
for row in seats:
    print("".join(row))
print("Free:", sum(row.count(".") for row in seats))
print("Snapshot:")
for row in snapshot:
    print("".join(row))
