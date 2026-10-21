n = int(input())
x = int(input())
largest = x
smallest = x
for _ in range(n - 1):
    x = int(input())
    if x > largest:
        largest = x
    if x < smallest:
        smallest = x
print("max", largest)
print("min", smallest)
