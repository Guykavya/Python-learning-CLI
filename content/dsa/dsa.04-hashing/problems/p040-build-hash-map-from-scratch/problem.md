# Build a hash map from scratch

Build the structure that Python's `dict` hides: a **hash table with chaining** that resizes itself. You may **not** use `dict`,
`set`, `Counter`, `defaultdict` or `{ }` braces: the test reads your source and fails if any of them appears (comments are ignored). Use a
list of buckets, and lists inside the buckets.

## The table

- It starts with `m = 8` buckets. Keys are **non-negative integers**; the bucket of a key is `key % m`.
- A bucket is a **chain**. A new key is **appended** to the end of its chain. Putting an existing key replaces its value (and never resizes).
- After inserting a **new** key, if `size * 4 > m * 3` (the load factor exceeds 0.75), **double** `m` and **rehash**: take every
  key (old bucket 0 first, chains left to right) and insert it into the new table with the new `key % m`.
- Deleting never shrinks the table.

## Commands

| command | effect and output |
|---|---|
| `put k v` | store `v` for `k`. No output. |
| `get k` | print the value, or `none` if the key is missing. |
| `del k` | remove the key and print `ok`, or print `missing`. |
| `size` | print the number of keys. |
| `buckets` | print the current number of buckets `m`. |
| `maxchain` | print the length of the longest chain (0 for an empty table). |

## Input

- Line 1: `q`.
- Next `q` lines: one command each.

## Output

One line per command that prints something.

## Example

Input:

```
10
put 0 1
put 8 2
put 16 3
maxchain
get 8
get 9
del 8
del 8
size
buckets
```

Output:

```
3
2
none
ok
missing
2
8
```

Keys 0, 8 and 16 all have remainder 0 modulo 8: they share bucket 0, so `maxchain` is 3.

## Constraints

- `1 <= q <= 200000`
- `0 <= k, v <= 10^9`
