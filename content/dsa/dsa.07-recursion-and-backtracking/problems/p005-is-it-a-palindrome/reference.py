def is_palindrome(s):
    def check(lo, hi):
        if lo >= hi:
            return True
        if s[lo] != s[hi]:
            return False
        return check(lo + 1, hi - 1)

    return check(0, len(s) - 1)
