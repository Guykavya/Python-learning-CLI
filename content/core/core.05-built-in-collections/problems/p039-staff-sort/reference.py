rows = []
for _ in range(int(input())):
    name, dept, salary = input().split()
    rows.append((dept, -int(salary), name))
rows.sort()
for dept, neg, name in rows:
    print(dept, name, -neg)
