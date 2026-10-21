word = input().strip()
for pos, ch in enumerate(word):
    if ch.lower() in "aeiou":
        print(f"First vowel '{ch}' at position {pos}")
        break
else:
    print("No vowels")
