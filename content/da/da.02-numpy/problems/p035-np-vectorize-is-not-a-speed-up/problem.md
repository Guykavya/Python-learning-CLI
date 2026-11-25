# `np.vectorize` is not a speed-up

Chapter sections 12.1–12.3. A colleague has two million parcel weights (kg) in a `float64` array `weights` and a fee rule written for one parcel:

```python
def shipping_fee(weight):
    if weight <= 1.0:
        return 40.0
    elif weight <= 5.0:
        return 40.0 + (weight - 1.0) * 15.0
    else:
        return 100.0 + (weight - 5.0) * 25.0

fee_all = np.vectorize(shipping_fee)
fees = fee_all(weights)
```

The colleague says: "I used `np.vectorize`, so now it is vectorised and runs in C like any NumPy function. Problem solved."

In `answer.md` write about 200 to 350 words:

1. Explain what `np.vectorize` really does when `fee_all(weights)` runs, and why it is not much faster than a `for` loop.
2. Say what `np.vectorize` *is* good for.
3. Rewrite the fee rule so that the work really happens inside NumPy (show the code; `np.where` or `np.select`).
4. Explain why your version is fast: what runs per element, and where.
5. Say how you would **prove** the speed-up to the colleague, and check that both versions agree.
6. Name one kind of function for which `np.vectorize` is a reasonable choice.

Use the words *ufunc*, *Python function*, *convenience* and *measure*.

## Example

A good answer starts from what happens per element: "For each of the two million weights, `np.vectorize` calls `shipping_fee`, a Python function..."
