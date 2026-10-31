# Seeded shuffle, sample and dice

Random choices in tests, games and data science must often be **reproducible**: the same seed
must give the same result every time, on every computer. The way to do that is a private
generator, `rng = random.Random(seed)`, instead of the module-level functions
(`random.shuffle`, `random.seed`, ...), which share one hidden global generator with every other
piece of code in the program.

The numbers are fixed by the seed: `random.Random` uses the Mersenne Twister algorithm, and the
Python documentation promises that the same integer seed gives the same underlying sequence in
every version and on every platform. `shuffle`, `sample` and `randint` are built on that sequence
and have not changed for many versions (3.11 to 3.14 give identical results), so the tests can
check exact values.

Write in `solution.py` (each function makes its **own** `random.Random(seed)`):

1. `shuffled(items, seed) -> list`: a new list with the items in random order (`rng.shuffle` on a copy).
   The caller's list must not change.
2. `pick_winners(names, k, seed) -> list[str]`: `k` **different** names (`rng.sample`). If `k` is
   larger than the number of names, `sample` raises `ValueError`; let it.
3. `roll_dice(n, seed) -> list[int]`: `n` rolls of a six-sided die, using **one** generator and
   `rng.randint(1, 6)` for each roll.
4. `split_data(items, test_percent, seed) -> (train, test)`: shuffle a copy with
   `shuffled(items, seed)`; the first `len(items) * test_percent // 100` items are `test`, the rest
   are `train`. Return `(train, test)`. A percent outside 0..100 raises `ValueError`.

The global generator must be left untouched: a test checks that `random.random()` gives the same
numbers before and after your functions run.

**Example**

```python
shuffled([1, 2, 3, 4, 5, 6, 7, 8], 42)                          # [4, 5, 7, 8, 3, 6, 1, 2]
pick_winners(["Asha", "Ben", "Chen", "Dev", "Esha", "Farah"], 3, 42)   # ['Farah', 'Asha', 'Esha']
roll_dice(10, 42)                                                # [6, 1, 1, 6, 3, 2, 2, 2, 6, 1]
split_data(list(range(10)), 30, 42)                              # ([8, 5, 6, 9, 4, 0, 1], [7, 3, 2])
```
