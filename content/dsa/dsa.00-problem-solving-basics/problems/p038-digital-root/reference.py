n = int(input())
rounds = 0
while n >= 10:
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    n = total
    rounds += 1
print(f"root {n}")
print(f"rounds {rounds}")
