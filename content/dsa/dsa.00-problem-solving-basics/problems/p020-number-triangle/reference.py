n = int(input())

for i in range(1, n + 1):
    line = ""
    for j in range(1, i + 1):
        if j > 1:
            line += " "
        line += str(j)
    print(line)
