def count_palindromes(s):
    total = 0
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):     # odd, even
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                total += 1
                lo -= 1
                hi += 1
    return total
