width = int(input())
words = input().split()
line = ""
count = 0
for word in words:
    if not line:
        line = word
    elif len(line) + 1 + len(word) <= width:
        line += " " + word
    else:
        print(line)
        count += 1
        line = word
if line:
    print(line)
    count += 1
print(f"Lines: {count}")
