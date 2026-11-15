s = input().strip()
k = int(input())

count = {}        # character -> how many times it is inside the window s[left..right]
left = 0
best = 0          # longest window with at most k distinct characters
total = 0         # number of substrings with at most k distinct characters

for right in range(len(s)):
    ch = s[right]
    count[ch] = count.get(ch, 0) + 1
    while len(count) > k:
        out = s[left]
        count[out] -= 1
        if count[out] == 0:
            del count[out]
        left += 1
    # now s[left..right] is the longest good window that ends at right
    best = max(best, right - left + 1)
    total += right - left + 1

print(best)
print(total)
