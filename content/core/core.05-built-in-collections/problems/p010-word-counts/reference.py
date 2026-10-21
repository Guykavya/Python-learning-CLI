counts = {}
for w in input().lower().split():
    counts[w] = counts.get(w, 0) + 1
if not counts:
    print("No words.")
for word, n in counts.items():
    print(f"{word}: {n}")
