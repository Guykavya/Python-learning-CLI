balance = int(input())
n = int(input())

for _ in range(n):
    op = input()
    amount = int(input())
    if op != "D" and op != "W":
        print("unknown operation")
    elif amount <= 0:
        print("invalid amount")
    elif op == "W" and amount > balance:
        print("declined")
    else:
        if op == "D":
            balance += amount
        else:
            balance -= amount
        print("balance", balance)

print("final", balance)
