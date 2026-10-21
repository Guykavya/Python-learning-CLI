n = int(input())
ranked = []
for _ in range(n):
    name, score = input().split()
    ranked.append((-int(score), name))
ranked.sort()
if not ranked:
    print("No scores.")
for place, (neg, name) in enumerate(ranked[:3], start=1):
    print(f"{place}. {name} {-neg}")
