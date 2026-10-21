UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
n = int(input())
valid = 0
for _ in range(n):
    code = input().strip()
    if len(code) != 7:
        reason = "length"
    elif not all(ch in UPPER for ch in code[:2]):
        reason = "letters"
    elif code[2] != "-":
        reason = "dash"
    elif not all(ch in DIGITS for ch in code[3:]):
        reason = "digits"
    else:
        reason = ""
    if reason:
        print(f"{code}: invalid ({reason})")
    else:
        print(f"{code}: valid")
        valid += 1
print(f"Valid: {valid} of {n}")
