password = input()
long_enough = len(password) >= 8
has_digit = any(ch.isdigit() for ch in password)
has_capital = any(ch.isupper() for ch in password)
only_alnum = all(ch.isalnum() for ch in password)
for label, ok in zip(["Length 8+", "Has digit", "Has capital", "Only letters and digits"],
                     [long_enough, has_digit, has_capital, only_alnum]):
    print(f"{label}: {'yes' if ok else 'no'}")
print("Strong" if all([long_enough, has_digit, has_capital, only_alnum]) else "Weak")
