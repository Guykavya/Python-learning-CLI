balance = int(input())
count = 0
while True:
    line = input().strip()
    if line == "end":
        break
    if not (len(line) >= 2 and line[0] in "+-" and line[1:].isdigit()):
        print(f"Skipped: {line}")
        continue
    count += 1
    amount = int(line[1:])
    if line[0] == "-" and amount > balance:
        print(f"#{count} declined: balance {balance}, needed {amount}")
        break
    balance += amount if line[0] == "+" else -amount
    print(f"#{count} OK, balance {balance}")
print(f"Final balance: {balance}")
