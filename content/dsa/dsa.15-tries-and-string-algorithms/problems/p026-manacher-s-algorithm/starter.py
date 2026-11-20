def manacher(s):
    """p[i] = palindrome radius at position i of '#' + '#'.join(s) + '#'."""
    t = "#" + "".join(ch + "#" for ch in s)       # length 2n + 1, also for s = ""
    p = [0] * len(t)
    for i in range(len(t)):                      # expand around every centre from scratch: O(n**2)
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < len(t) and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
    return p


def count_palindromes(s):
    """Number of palindromic substrings, counted by position."""
    return 0
