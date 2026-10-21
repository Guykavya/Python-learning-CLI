goal = int(input())
deposit = int(input())
rate = float(input())

if goal > 0 and deposit == 0:
    print("Goal not reachable")
else:
    balance = 0.0
    months = 0
    while balance < goal:
        balance += balance * rate / 100
        balance += deposit
        months += 1
    print(f"Months: {months}")
    print(f"Balance: {balance:.2f}")
