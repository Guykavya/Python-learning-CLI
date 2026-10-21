words = input().split()
if not words:
    print("No words")
else:
    shortest = min(words, key=len)
    for i, ch in enumerate(shortest):
        if not all(w[i] == ch for w in words):
            prefix = shortest[:i]
            break
    else:
        prefix = shortest
    print(f"Prefix: {prefix if prefix else '(none)'}")
    print(f"Length: {len(prefix)}")
