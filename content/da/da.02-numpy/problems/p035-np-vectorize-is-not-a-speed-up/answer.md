## Model answer

**What `np.vectorize` does.** It is a **convenience** wrapper, not a compiler. When `fee_all(weights)` runs, NumPy loops over the two million weights and calls the **Python function** `shipping_fee` once per element: two million Python calls, each with its own `if` checks, float objects and return value. The NumPy documentation says it plainly: it is provided for convenience, not performance, and is essentially a `for` loop. So the code is about as slow as the loop it replaced; in Ch. 12.3 it was 33 times slower than the ufunc version of a sigmoid (machine-specific timing).

**What it is good for.** It gives a scalar function the array interface: it accepts arrays, broadcasts its arguments and returns an array of the right shape, so the rest of the code can stay array-shaped.

**A real vectorised version.** Replace the `if`/`elif` by masks and the arithmetic by array arithmetic:

```python
w = weights
fees = np.select(
    [w <= 1.0, w <= 5.0],
    [40.0, 40.0 + (w - 1.0) * 15.0],
    default=100.0 + (w - 5.0) * 25.0,
)
```

(Two nested `np.where` calls do the same.)

**Why it is fast.** Every piece is a **ufunc** or a NumPy routine (`<=`, `-`, `*`, `+`, `select`) that runs one tight loop in C over the whole array of `float64` values: no Python call, no type check, no new Python object per element. All three formulas are computed for every weight and `select` picks one per element; doing a few full-array passes in C is still far cheaper than two million Python calls.

**How to prove it.** **Measure**: time both versions on realistic data with `time.perf_counter()` or `timeit`, taking the best of several runs (Ch. 17.5), and check they agree first with `np.allclose(fees_vectorize, fees_select)`, including weights exactly at 1.0 and 5.0 where `<=` matters.

**When `np.vectorize` is fine.** When the per-element work cannot be written with array operations (parsing a messy string, a lookup that may raise an exception) and the data is small, or when speed does not matter and you only want broadcasting.

**Checklist: your answer should mention**
- [ ] `np.vectorize` calls the **Python function** once per element (a loop in disguise)
- [ ] it is a **convenience** (array interface, broadcasting), not a speed-up
- [ ] real speed comes from **ufuncs** and array operations running in C
- [ ] the rewrite with **`np.where` / `np.select`** (masks replace `if`/`elif`)
- [ ] **measure** both versions and check they give the same results (band edges included)
- [ ] a case where `np.vectorize` is acceptable (non-arithmetic logic, small data)
