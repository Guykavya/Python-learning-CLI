- Saying "lists are too big to cache". Size is not the problem; changeability is.
- Suggesting `str(prices)` as the key. It works by accident and breaks for values whose `str` is the same but which are different.
- Fixing the error with a tuple but not mentioning that the cached function must also be pure.
- Thinking `cache_clear()` after every change of `stock` is a real fix. It works, but it is easy
  to forget; a function that depends on changing data should usually not be cached.
- Saying the second `stock_of` call "recomputes but gets 5". It does not run the body at all: it is a hit.
