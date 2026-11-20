def longest_pal_dp(s):
    n = len(s)
    if n == 0:
        return ""
    is_pal = [[False] * n for _ in range(n)]
    start, best = 0, 1
    for i in range(n):
        is_pal[i][i] = True                       # length 1
    for length in range(2, n + 1):                # shorter substrings first
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
                if length > best:                 # strictly longer: keeps the leftmost
                    start, best = i, length
    return s[start:start + best]


def longest_pal_expand(s):
    best = ""
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):    # odd, even length
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1
                hi += 1
            if hi - lo - 1 > len(best):
                best = s[lo + 1:hi]
    return best
