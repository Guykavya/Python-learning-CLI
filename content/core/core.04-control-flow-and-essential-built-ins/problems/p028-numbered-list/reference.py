line = input()
if not line.strip():
    print("(no items)")
else:
    items = line.split(",")
    for number, item in enumerate(items, start=1):
        print(f"{number}. {item.strip()}")
    word = "item" if len(items) == 1 else "items"
    print(f"Total: {len(items)} {word}")
