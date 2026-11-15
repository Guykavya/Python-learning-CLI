def kth_permutation(n, k):
    digits = list(range(1, n + 1))
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    k -= 1
    out = []
    for size in range(n - 1, -1, -1):
        i, k = divmod(k, fact[size])
        out.append(str(digits.pop(i)))
    return "".join(out)
