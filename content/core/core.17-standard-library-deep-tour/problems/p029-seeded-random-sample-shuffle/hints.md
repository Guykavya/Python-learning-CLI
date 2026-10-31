## Hint 1

`rng = random.Random(42)` creates an independent generator. It has the same methods as the
module: `rng.shuffle(lst)`, `rng.sample(population, k)`, `rng.randint(a, b)`. Why is
`random.seed(42); random.shuffle(lst)` not acceptable, even though it gives the same order?

## Hint 2

`shuffle` changes a list **in place** and returns `None`. So copy first (`list(items)`), shuffle
the copy, return the copy. For the dice, where should the `Random(seed)` be created: inside the
loop or before it? What would each roll be if you created it inside?

## Hint 3

```
shuffled:     result = list(items); Random(seed).shuffle(result); return result
pick_winners: return Random(seed).sample(names, k)
roll_dice:    rng = Random(seed); return [rng.randint(1, 6) for each of n]
split_data:   check 0 <= p <= 100
              mixed = shuffled(items, seed); n_test = len(mixed) * p // 100
              return mixed[n_test:], mixed[:n_test]
```
