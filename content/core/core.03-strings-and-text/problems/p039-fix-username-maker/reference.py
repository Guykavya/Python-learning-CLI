# Username maker (fixed).
name = input()
year = input().strip()
words = name.split()
first = words[0].lower()
last = words[-1]
username = first + last[0].lower() + year[-2:]
print(f"Hello, {' '.join(words).title()}!")
print(f"Username: {username}")
print(f"Age in 2026: {2026 - int(year)}")
