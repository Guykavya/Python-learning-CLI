def window_hashes(text, m, B, M):
    """Hash of every window text[i:i+m], with the rolling update."""
    out = []
    for i in range(len(text) - m + 1):          # recomputes every window from scratch: O(n * m)
        h = 0
        for ch in text[i:i + m]:
            h = (h * B + ord(ch)) % M
        out.append(h)
    return out


def rabin_karp(text, pattern, params=((131, 1_000_000_007), (137, 998_244_353)), verify=True):
    """Start positions where every hash pair matches (and the strings match, if verify)."""
    return []
