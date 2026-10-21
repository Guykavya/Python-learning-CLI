a = int(input())
b = int(input())
step = 1 if a <= b else -1
line = ""
for n in range(a, b + step, step):
    line += f"{n} "
print(line.strip())
