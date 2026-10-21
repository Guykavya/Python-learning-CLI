words = input().split()
if not words:
    print("(nothing)")
else:
    print(" ".join(reversed(words)))
    line = ""
    for word in words:
        backwards = ""
        for ch in reversed(word):
            backwards += ch
        line += backwards + " "
    print(line.strip())
