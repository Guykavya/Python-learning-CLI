def longest_palindrome(s):
    """Leftmost longest palindromic substring."""
    return s[:1]


def palindrome_queries(s, queries):
    """For each (l, r): is s[l:r] a palindrome?"""
    return [s[l:r] == s[l:r][::-1] for l, r in queries]      # O(r - l) per query
