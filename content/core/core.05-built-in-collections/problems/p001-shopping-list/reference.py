items = []
while True:
    line = input()
    if line == "done":
        break
    items.append(line)
print(f"Items: {len(items)}")
if not items:
    print("The list is empty.")
for i, item in enumerate(items, start=1):
    print(f"{i}. {item}")
