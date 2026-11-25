## Hint 1

What does `np.array_split` do when `n` is not divisible by `k`? Which folds get the extra row?

## Hint 2

Shuffle once with a generator built from the seed, then split the shuffled indices.
