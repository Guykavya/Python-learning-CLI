c = int(input())
even = 0
odd = 0
for _ in range(c):
    x = int(input())
    if x % 2 == 0:
        even += 1
    else:
        odd += 1
print("even", even)
print("odd", odd)
