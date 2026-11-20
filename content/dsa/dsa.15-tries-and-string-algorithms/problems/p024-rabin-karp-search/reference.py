def window_hashes(text, m, B, M):
    n = len(text)
    if m > n:
        return []
    top = pow(B, m - 1, M)                       # B**(m-1) mod M, computed once
    h = 0
    for ch in text[:m]:
        h = (h * B + ord(ch)) % M
    out = [h]
    for i in range(n - m):
        h = ((h - ord(text[i]) * top) * B + ord(text[i + m])) % M    # drop text[i], add text[i+m]
        out.append(h)
    return out


def string_hash(s, B, M):
    h = 0
    for ch in s:
        h = (h * B + ord(ch)) % M
    return h


def rabin_karp(text, pattern, params=((131, 1_000_000_007), (137, 998_244_353)), verify=True):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    if m > len(text):
        return []
    lists = [window_hashes(text, m, B, M) for B, M in params]
    wanted = [string_hash(pattern, B, M) for B, M in params]
    found = []
    for i in range(len(text) - m + 1):
        if all(hs[i] == w for hs, w in zip(lists, wanted)):
            if not verify or text[i:i + m] == pattern:
                found.append(i)
    return found
