# Why all() of nothing is True

`any([])` is `False` but `all([])` is `True`. Many people think this is a mistake in Python.

Write an explanation in `answer.md` that covers:

1. What `any` and `all` do, written as the loops they are equivalent to.
2. Why `all` of an empty iterable must be `True` and `any` must be `False`, using the loops
   from point 1 and one everyday example.
3. That both short-circuit, with an example showing where it matters.
4. A real bug this can cause when checking user input, and how to fix it.
5. How this fits with `sum([])` being `0` and `max([])` raising an error.
