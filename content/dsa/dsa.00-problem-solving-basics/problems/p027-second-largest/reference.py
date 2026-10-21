n = int(input())

first = int(input())
second = 0
has_second = False

for _ in range(n - 1):
    x = int(input())
    if x > first:
        second = first
        has_second = True
        first = x
    elif x < first and (not has_second or x > second):
        second = x
        has_second = True

if has_second:
    print(second)
else:
    print("none")
