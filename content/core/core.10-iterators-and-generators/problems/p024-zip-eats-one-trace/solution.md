## Approach

`zip` builds each tuple by calling `next()` on its inputs from left to right.

**First half** (`zip(it, letters)`): tuples `(1, 'a')` and `(2, 'b')` are made as expected, each
after its `give` line. For the third tuple, `zip` first asks `it`, which prints `give 3` and hands
over 3. Then it asks `letters`, which is finished. `zip` stops, and the 3 is **thrown away**.
`list(it)` then gives only `[4, 5]`, printing `give 4` and `give 5` before the `left:` line
(the list must be built before `print` can run).

**Second half** (`zip(letters, it)`): for the third tuple `zip` asks `letters` first, finds it
finished, and stops **without** touching `it`. So nothing is lost: `left: [3, 4, 5]`.

## Output

```text
give 1
(1, 'a')
give 2
(2, 'b')
give 3
give 4
give 5
left: [4, 5]
---
give 1
('a', 1)
give 2
('b', 2)
give 3
give 4
give 5
left: [3, 4, 5]
```

## Complexity

O(n).

## Another way

If you need the leftover items, put the shorter or "length-limiting" input first in `zip`, or
use `itertools.zip_longest`. In Python 3.10+, `zip(a, b, strict=True)` raises an error when the
lengths differ, which turns this silent loss into a loud bug.
