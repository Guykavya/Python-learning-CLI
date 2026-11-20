def longest_pal_subseq(s):
    n = len(s)
    if n == 0:
        return ""
    f = [[0] * n for _ in range(n)]          # f[i][j] = LPS length inside s[i..j]
    for i in range(n):
        f[i][i] = 1
    for length in range(2, n + 1):           # short ranges first
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                f[i][j] = (f[i + 1][j - 1] if length > 2 else 0) + 2
            else:
                f[i][j] = max(f[i + 1][j], f[i][j - 1])

    left, right, middle = [], [], ""
    i, j = 0, n - 1
    while i <= j:
        if i == j:                           # one letter in the middle
            middle = s[i]
            break
        if s[i] == s[j]:                     # both ends belong to the palindrome
            left.append(s[i])
            right.append(s[j])
            i += 1
            j -= 1
        elif f[i + 1][j] >= f[i][j - 1]:     # drop the left end
            i += 1
        else:                                # drop the right end
            j -= 1
    return "".join(left) + middle + "".join(reversed(right))
