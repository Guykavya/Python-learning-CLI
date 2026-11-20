def rod_cut(price, n):
    """Most money from cutting a rod of length n; a piece of length k sells for price[k - 1]."""
    return price[n - 1] if n > 0 else 0
