# One seed, many streams

Chapter sections 13.2 and 13.5. A team runs a simulation in 8 worker processes and wants the whole run to be reproducible from **one** seed. Three proposals:

```python
# A: a seed per worker, made by adding the worker number
rngs = [np.random.default_rng(seed + i) for i in range(8)]

# B: one generator, handed to every worker
rng = np.random.default_rng(seed)
rngs = [rng] * 8          # each process receives its own pickled copy of rng

# C: spawn children from one seed sequence
rngs = [np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(8)]
```

A colleague ran proposal A twice, once with `seed = 100` and once with `seed = 101`, and printed two numbers from the first four workers:

```python
a = [np.random.default_rng(100 + i).random(2).round(4).tolist() for i in range(4)]
b = [np.random.default_rng(101 + i).random(2).round(4).tolist() for i in range(4)]
print(a)
print(b)
```
```text
[[0.835, 0.5966], [0.9435, 0.3594], [0.16, 0.5859], [0.3127, 0.2243]]
[[0.9435, 0.3594], [0.16, 0.5859], [0.3127, 0.2243], [0.8386, 0.6921]]
```

(Output measured with NumPy 2.5.4; another version may print other numbers, but the pattern is the same.)

In `answer.md` write about 200 to 350 words:

1. Explain what the printed output shows about proposal A, and why that is a problem when you compare runs with different seeds.
2. Explain what goes wrong with proposal B when each worker process gets a copy of the same generator.
3. Explain why proposal C gives **independent streams** and is still **reproducible** from the one seed.
4. Say what each worker should do with its own generator, and what it must not do.

Use the words *independent streams*, *reproducible*, *spawn* and *state*.

## Example

"In proposal A, run 101's worker 0 produces exactly the numbers of run 100's worker 1..."
