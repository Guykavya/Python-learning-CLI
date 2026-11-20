def manacher(s):
    t = "#" + "".join(ch + "#" for ch in s)       # length 2n + 1, also for s = ""
    n = len(t)
    p = [0] * n
    c = r = 0                                    # centre and right edge of the rightmost palindrome
    for i in range(n):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])      # copy from the mirror, capped at the edge
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1                            # expand beyond what is known
        if i + p[i] > r:
            c, r = i, i + p[i]
    return p


def count_palindromes(s):
    return sum((x + 1) // 2 for x in manacher(s))
