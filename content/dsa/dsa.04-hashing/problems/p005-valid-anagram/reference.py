s = input().strip()
t = input().strip()

def table(word):
    count = {}
    for ch in word:
        count[ch] = count.get(ch, 0) + 1
    return count

print("YES" if table(s) == table(t) else "NO")
