total = 0
count = 0

x = int(input())
while x != 0:
    total += x
    count += 1
    print(f"{total / count:.2f}")
    x = int(input())

print("count", count)
