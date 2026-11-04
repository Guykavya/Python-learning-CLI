s = input().strip()

count = {}
for ch in s:
    count[ch] = count.get(ch, 0) + 1

answer = -1
for i, ch in enumerate(s):
    if count[ch] == 1:
        answer = i
        break
print(answer)
