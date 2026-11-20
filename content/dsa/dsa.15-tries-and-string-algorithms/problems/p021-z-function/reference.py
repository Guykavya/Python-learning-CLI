def z_function(s):
    n = len(s)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l, r = 0, 0                              # the Z-box is s[l:r]
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])      # reuse the copy inside the box
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1                        # extend with new comparisons
        if i + z[i] > r:
            l, r = i, i + z[i]               # a new rightmost box
    return z
