n = int(input())

for i in range(1, n + 1):
    line = " " * (n - i)
    # Going up: 1, 2, ..., i
    for v in range(1, i + 1):
        line += f"{v % 10}"
    # Coming down: i - 1, ..., 1
    for v in range(i - 1, 0, -1):
        line += f"{v % 10}"
    print(line)
