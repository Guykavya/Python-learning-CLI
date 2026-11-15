def reverse(s):
    if s == "":
        return ""
    return reverse(s[1:]) + s[0]
