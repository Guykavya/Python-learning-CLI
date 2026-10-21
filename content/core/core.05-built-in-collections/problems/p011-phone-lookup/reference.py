book = {}
for _ in range(int(input())):
    name, number = input().split()
    book[name] = number
for _ in range(int(input())):
    name = input().strip()
    if name in book:
        print(book[name])
    else:
        print(f"Not found: {name}")
