- Calling snippet 1 "a bug in `append`". The list is shared because the default is evaluated once.
- Saying "bare `except` is bad because it is slow". The cost is hidden bugs, not speed.
- Fixing 4 with `str.join` but forgetting to turn the numbers into strings (`str(row.score)`).
- Saying `+=` on strings is always slow. CPython has a shortcut that often hides it; but it is not
  guaranteed, so `join` is the safe habit.
- Naming a smell without the fix, or a fix without the reason. Give all three parts.
- For 6, "return `None` and test with `if user:`". A falsy valid object would hide; use `is None`.
