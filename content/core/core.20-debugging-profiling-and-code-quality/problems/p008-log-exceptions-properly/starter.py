def safe_divide_all(pairs, logger) -> list:
    """Divide each (a, b); log problems instead of stopping."""
    results = []
    for a, b in pairs:
        try:
            results.append(a / b)
        except Exception as e:
            print("error:", e)
            results.append(None)
    return results
