def word_break(s, words):
    word_set = set(words)
    longest = max((len(w) for w in word_set), default=0)
    n = len(s)
    f = [False] * (n + 1)
    f[0] = True                                    # the empty prefix needs no cut
    for i in range(1, n + 1):
        for j in range(max(0, i - longest), i):
            if f[j] and s[j:i] in word_set:
                f[i] = True
                break
    return f[n]
