count = 0
total = 0.0
while True:
    line = input().strip()
    if line.lower() == "done":
        break
    count += 1
    total += float(line)
print(f"Items: {count}")
print(f"Total: {total:.2f}")
