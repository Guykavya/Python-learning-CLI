s = input()

seen = set()          # the characters inside the window s[l..r]
l = 0
best_len, best_start = 0, 0
for r in range(len(s)):
    while s[r] in seen:           # shrink until s[r] is no longer inside
        seen.remove(s[l])
        l += 1
    seen.add(s[r])
    if r - l + 1 > best_len:      # strictly longer: ties keep the earlier start
        best_len, best_start = r - l + 1, l

print(best_len)
print(s[best_start:best_start + best_len])
