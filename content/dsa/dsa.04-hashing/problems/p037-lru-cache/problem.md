# LRU cache

A **cache** keeps at most `c` key-value pairs. When it is full and a new key arrives, it throws out the **least recently used** key.
Both `get` and `put` count as a "use". Every operation must be `O(1)` on average.

Commands:

- `get k`: print the value of `k` and mark `k` as most recently used. Print `-1` if `k` is not in the cache.
- `put k v`: store `v` for `k` and mark `k` as most recently used. If `k` is new and the cache already has `c` keys, first evict
  the least recently used key. Updating an existing key never evicts anything.

Idea: a Python `dict` remembers insertion order. To refresh a key, **remove it and insert it again**, so it moves to the end. The first
key of the dictionary (`next(iter(cache))`) is always the least recently used one.

## Input

- Line 1: `c`.
- Line 2: `q`, the number of commands.
- Then `q` lines, each `get k` or `put k v` (integers).

## Output

One line for every `get`.

## Example

Input:

```
2
9
put 1 1
put 2 2
get 1
put 3 3
get 2
put 4 4
get 1
get 3
get 4
```

Output:

```
1
-1
-1
3
4
```

After `get 1`, key 2 is the least recently used, so `put 3 3` evicts 2 and `get 2` gives -1. Then `put 4 4` evicts 1.

## Constraints

- `1 <= c <= 100000`, `1 <= q <= 200000`
- `0 <= k, v <= 10^9`
