# Why is the array faster than the list?

Chapter sections 1.1 and 1.2. In Ch. 1.3 the sum of the squares of a million numbers took about 80 ms with a Python
loop over a list and about 3 ms with `(arr * arr).sum()` (machine-specific). Explain in `answer.md`, in about 150 to
250 words, **why** the array is so much faster. Answer these three questions:

1. How does a Python list of a million integers sit in memory, and how does a NumPy `int64` array of the same numbers?
2. What must the Python interpreter do for **each** step of `total += v * v`, and why does NumPy not need to do that?
3. When is the array *not* faster (the honest note in Ch. 1.3)?

## Example

A start: "A list does not hold the numbers themselves. It holds *pointers*, one per item, and each pointer leads to a
separate integer object somewhere else in memory..."
