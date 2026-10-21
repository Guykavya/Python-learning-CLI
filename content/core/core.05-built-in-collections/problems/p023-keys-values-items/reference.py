scores = {}
for _ in range(int(input())):
    name, score = input().split()
    scores[name] = int(score)
print("Names:", " ".join(scores.keys()))
print("Scores:", " ".join(str(v) for v in scores.values()))
print("Total:", sum(scores.values()))
best = max(scores, key=scores.get)
print(f"Best: {best} ({scores[best]})")
