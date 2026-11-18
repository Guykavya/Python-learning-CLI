def decode_ways(s):
    n = len(s)
    f = [0] * (n + 1)
    f[0] = 1                                   # the empty prefix: one way (do nothing)
    for i in range(1, n + 1):
        if s[i - 1] != "0":                    # last piece is one digit
            f[i] += f[i - 1]
        if i >= 2 and 10 <= int(s[i - 2:i]) <= 26:   # last piece is two digits
            f[i] += f[i - 2]
    return f[n]
