note = input().strip()
magazine = input().strip()

stock = {}
for ch in magazine:
    stock[ch] = stock.get(ch, 0) + 1

answer = "YES"
for ch in note:
    if stock.get(ch, 0) == 0:
        answer = "NO"
        break
    stock[ch] -= 1
print(answer)
