target = input().strip()
sentence = input()
for n, word in enumerate(sentence.split(), start=1):
    if word.strip(".,!?").lower() == target.lower():
        print(f"Found '{target}' as word {n}")
        break
else:
    print(f"'{target}' not found")
