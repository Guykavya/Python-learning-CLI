def manacher(s):
    t = "#" + "".join(ch + "#" for ch in s)       # length 2n + 1, also for s = ""
    n = len(t)
    p = [0] * n
    c = r = 0
    for i in range(n):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
        if i + p[i] > r:
            c, r = i, i + p[i]
    return p


def longest_palindrome(s):
    p = manacher(s)
    best = 0
    for i in range(len(p)):
        if p[i] > p[best]:                       # strictly larger: keeps the leftmost
            best = i
    start = (best - p[best]) // 2
    return s[start:start + p[best]]


def palindrome_queries(s, queries):
    p = manacher(s)
    return [p[l + r] >= r - l for l, r in queries]   # the centre of s[l:r] is l + r in t
