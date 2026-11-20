def shortest_palindrome(s):
    """Shortest palindrome made by adding characters only at the front of s."""
    for k in range(len(s), -1, -1):          # longest palindromic prefix, the slow way: O(n**2)
        if s[:k] == s[:k][::-1]:
            return s[k:][::-1] + s
    return s
