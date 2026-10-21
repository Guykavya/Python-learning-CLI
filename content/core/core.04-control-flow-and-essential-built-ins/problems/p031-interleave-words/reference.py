a = input()
b = input()
result = ""
for x, y in zip(a, b):
    result += x + y
result += a[len(b):] + b[len(a):]
print(result if result else "(empty)")
