message = input()
width = int(input())
if width <= 0:
    print("invalid width")
else:
    result = ""
    for c in range(width):
        for pos in range(c, len(message), width):
            result += message[pos]
    print(result)
