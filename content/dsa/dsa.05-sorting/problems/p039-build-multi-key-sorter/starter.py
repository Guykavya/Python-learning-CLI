n = int(input())
rows = []
for _ in range(n):
    name, age, score = input().split()
    rows.append((name, int(age), int(score)))
k = int(input())
rules = []
for _ in range(k):
    field, direction = input().split()
    rules.append((field, direction))
# TODO: stable merge sort of rows following the rules (no sorted / .sort / cmp_to_key)
for name, age, score in rows:
    print(name, age, score)
