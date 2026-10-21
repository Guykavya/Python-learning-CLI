first_pos = {}
for i, word in enumerate(input().split(), start=1):
    if word in first_pos:
        print(f"{word} at {first_pos[word]} and {i}")
        break
    first_pos[word] = i
else:
    print("No repeats")
