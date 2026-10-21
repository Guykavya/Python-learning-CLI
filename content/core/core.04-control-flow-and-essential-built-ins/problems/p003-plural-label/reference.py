n = int(input())
noun = input().strip()
amount = "no" if n == 0 else str(n)
ending = "" if n == 1 else "s"
print(f"{amount} {noun}{ending}")
