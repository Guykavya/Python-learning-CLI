class StringHash:
    def __init__(self, s, B=131, M=(1 << 61) - 1):
        self.M = M
        self.H = [0] * (len(s) + 1)
        self.P = [1] * (len(s) + 1)
        for i, ch in enumerate(s):
            self.H[i + 1] = (self.H[i] * B + ord(ch)) % M
            self.P[i + 1] = (self.P[i] * B) % M

    def get(self, l, r):
        """Hash of s[l:r]."""
        return (self.H[r] - self.H[l] * self.P[r - l]) % self.M


def has_repeat(s, length, sh):
    """Start of a window of this length that occurred earlier, or -1."""
    seen = {}
    for i in range(len(s) - length + 1):
        h = sh.get(i, i + length)
        if h in seen:
            j = seen[h]
            if s[j:j + length] == s[i:i + length]:     # verify: never trust a hash alone
                return i
        else:
            seen[h] = i
    return -1


def longest_repeat(s):
    sh = StringHash(s)
    lo, hi, best = 1, len(s) - 1, ""
    while lo <= hi:
        mid = (lo + hi) // 2
        i = has_repeat(s, mid, sh)
        if i != -1:
            best = s[i:i + mid]
            lo = mid + 1                               # try longer
        else:
            hi = mid - 1                               # too long
    return best
