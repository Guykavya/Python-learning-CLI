# Use the standard library

Before you write a loop, ask: does the standard library already do this? Often it does, in
faster, tested code that other programmers recognise at a glance.

| You hand-write | The library has |
|---|---|
| a dict that counts | `collections.Counter` (`.most_common(n)`) |
| `if k not in d: d[k] = []` | `collections.defaultdict(list)` |
| a list used as a queue with `pop(0)` | `collections.deque` with `popleft()` |
| counting runs of equal neighbours | `itertools.groupby` |
| nested loops to join lists | `itertools.chain` |
| a recursive function that repeats work | `functools.cache` |

`starter.py` has seven working functions that do everything by hand. Copy it to `solution.py`
and replace each with the right tool. Keep names and parameters; behaviour must not change.

The tests check behaviour, and also that `Counter`, `defaultdict`, `deque`, `groupby`, `chain`
are used inside the matching functions and `count_paths` is decorated with `cache`/`lru_cache`.
They also check that `word_counts`, `top_words`, `run_lengths` and `join_all` contain no
`for`/`while` statement, that `group_by_length` has no `in` test, and that `bfs_order` does
not call `pop(0)`.

**Example**

```python
word_counts("the cat The")        # {'the': 2, 'cat': 1}
top_words("a b a c", 1)           # [('a', 2)]
run_lengths("aaabcc")             # [('a', 3), ('b', 1), ('c', 2)]
join_all([1, 2], [3])             # [1, 2, 3]
count_paths(5)                    # 8
```
