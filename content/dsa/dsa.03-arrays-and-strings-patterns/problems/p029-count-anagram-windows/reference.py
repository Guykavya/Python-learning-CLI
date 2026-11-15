text = input()
pattern = input()
n, m = len(text), len(pattern)

need = [0] * 26
for ch in pattern:
    need[ord(ch) - ord("a")] += 1

have = [0] * 26
count = 0
for r in range(n):
    have[ord(text[r]) - ord("a")] += 1          # character entering the window
    if r >= m:
        have[ord(text[r - m]) - ord("a")] -= 1  # character leaving the window
    if r >= m - 1 and have == need:             # the window text[r-m+1 .. r] is full
        count += 1

print(count)
