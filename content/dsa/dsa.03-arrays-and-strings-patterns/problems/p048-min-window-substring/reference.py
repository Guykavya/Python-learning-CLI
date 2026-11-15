s = input().strip()
t = input().strip()

need = {}
for ch in t:
    need[ch] = need.get(ch, 0) + 1

have = {}
missing = len(t)          # how many characters of t (with multiplicity) the window still lacks
left = 0
best_len, best_start = len(s) + 1, -1

for right in range(len(s)):
    ch = s[right]
    have[ch] = have.get(ch, 0) + 1
    if have[ch] <= need.get(ch, 0):
        missing -= 1
    while missing == 0:
        if right - left + 1 < best_len:          # strict: keep the earliest of equal lengths
            best_len, best_start = right - left + 1, left
        out = s[left]
        have[out] -= 1
        if have[out] < need.get(out, 0):
            missing += 1
        left += 1

if best_start == -1:
    print(-1)
else:
    print(s[best_start:best_start + best_len])
