# Last stone weight II

You have stones with positive integer weights. In one move you pick **any two** stones, with weights `x <= y`, and smash them together:

- if `x == y`, both stones are destroyed;
- otherwise the stone of weight `x` is destroyed and the other one now weighs `y - x`.

You keep smashing until at most one stone is left. Write `last_stone_weight_ii(stones)` that returns the **smallest possible** weight of the last stone, or `0` if no stone is left. You choose the pairs.

## Example

```python
>>> last_stone_weight_ii([2, 7, 4, 1, 8, 1])
1
>>> last_stone_weight_ii([31, 26, 33, 21, 40])
5
>>> last_stone_weight_ii([5])
5
>>> last_stone_weight_ii([3, 3])
0
```

One way for the first example: smash 2 and 4 (leaves 2), 7 and 8 (leaves 1), 2 and 1 (leaves 1), 1 and 1 (nothing), and the last stone is the other 1.

## Constraints

- `1 <= len(stones) <= 100`, `1 <= stones[i] <= 100`.
- Simulating every order of smashing is hopeless beyond 8 stones. Find the DP of chapter section 12 hidden in this story.

## Think about

Write the final weight as a sum of all the stones, each with a `+` or a `-` in front. (Smashing `y` and `x` leaves `y - x`; smash that with `z` and you get `z - (y - x)` or `(y - x) - z`.) Which problem from this module counts or finds such sign patterns? What does it mean for the final weight to be as small as possible?
