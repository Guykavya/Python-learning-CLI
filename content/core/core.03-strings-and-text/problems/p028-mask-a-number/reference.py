digits = input().replace(" ", "").replace("-", "")
print(f"Digits: {len(digits)}")
print(f"Masked: {digits[-4:].rjust(len(digits), '*')}")
