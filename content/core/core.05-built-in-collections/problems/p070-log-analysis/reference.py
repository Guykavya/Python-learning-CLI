n = int(input())
users = set()
page_count = {}
day_users = {}
day_count = {}
for _ in range(n):
    day, user, page = input().split()
    day = int(day)
    users.add(user)
    page_count[page] = page_count.get(page, 0) + 1
    day_users.setdefault(day, set()).add(user)
    day_count[day] = day_count.get(day, 0) + 1
print("Events:", n)
if n:
    print("Distinct users:", len(users))
    print("Top pages:")
    for neg, page in sorted((-c, p) for p, c in page_count.items())[:3]:
        print(f"  {page} {-neg}")
    day_sets = list(day_users.values())
    loyal = set(day_sets[0])
    for s in day_sets[1:]:
        loyal &= s
    print("Loyal users:", " ".join(sorted(loyal)) if loyal else "none")
    neg, day = min((-c, d) for d, c in day_count.items())
    print(f"Busiest day: {day} ({-neg})")
