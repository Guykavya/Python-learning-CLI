def z_function(s):
    """z[i] = length of the longest common prefix of s and s[i:]; z[0] = len(s)."""
    n = len(s)
    z = [0] * n
    if n:
        z[0] = n
    for i in range(1, n):
        k = 0
        while i + k < n and s[k] == s[i + k]:    # from scratch at every i: O(n**2)
            k += 1
        z[i] = k
    return z
