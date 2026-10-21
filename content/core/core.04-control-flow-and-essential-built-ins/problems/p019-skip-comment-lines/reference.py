total = 0
kept = 0
while True:
    line = input()
    if line == "END":
        break
    total += 1
    text = line.strip()
    if not text or text.startswith("#"):
        continue
    kept += 1
    print(f"{kept}: {text}")
print(f"Kept {kept} of {total} lines")
