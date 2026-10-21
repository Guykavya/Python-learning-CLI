groups = {}
for word in input().split():
    groups.setdefault(word[0].lower(), []).append(word)
for letter, words in groups.items():
    print(f"{letter}: {' '.join(words)}")
