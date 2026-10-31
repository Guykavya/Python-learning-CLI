def windows(iterable, k):
    window = ()
    for item in iterable:
        window = window + (item,)
        if len(window) > k:
            window = window[1:]
        if len(window) == k:
            yield window
