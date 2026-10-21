groups = {}
seen = set()
for word in input().split():
    if word in seen:
        continue
    seen.add(word)
    key = "".join(sorted(word))
    groups.setdefault(key, []).append(word)
if not groups:
    print("No words.")
for words in groups.values():
    print(" ".join(words))
