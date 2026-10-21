words = input().split()
if not words:
    print("No words")
else:
    longest = max(words, key=len)
    shortest = min(words, key=len)
    for label, word in (("Longest", longest), ("Shortest", shortest)):
        unit = "letter" if len(word) == 1 else "letters"
        print(f"{label}: {word} ({len(word)} {unit})")
