# Edit distance operations

A spell checker shows **how** to fix a word, not only how far it is. Write `edit_ops(a, b)` that returns a shortest list of operations that turns `a` into `b` (chapter section 15, "Reading the operations back").

Each operation is a tuple, and the operations are applied **one after another, in list order**. A position always refers to the string **as it is at that moment** (after the earlier operations):

| operation | effect on the current string `s` |
|---|---|
| `("insert", p, ch)` | `s = s[:p] + ch + s[p:]`, with `0 <= p <= len(s)` |
| `("delete", p)` | `s = s[:p] + s[p + 1:]`, with `0 <= p < len(s)` |
| `("replace", p, ch)` | `s = s[:p] + ch + s[p + 1:]`, with `0 <= p < len(s)` |

`ch` is a single character. The list must have exactly `edit_distance(a, b)` operations (p057), so it is as short as possible.

## Example

```python
>>> edit_ops("horse", "ros")
[('delete', 4), ('delete', 2), ('replace', 0, 'r')]
>>> edit_ops("kitten", "sitting")
[('insert', 6, 'g'), ('replace', 4, 'i'), ('replace', 0, 's')]
>>> edit_ops("", "ab")
[('insert', 0, 'b'), ('insert', 0, 'a')]
>>> edit_ops("abc", "abc")
[]
```

Check the first one: `"horse"` -> delete position 4 -> `"hors"` -> delete position 2 -> `"hos"` -> replace position 0 by `r` -> `"ros"`. Three operations, the edit distance.

There are often several shortest lists, and any of them is accepted. The tests **apply** your operations to `a` and check that the result is `b`, that every position is valid at its moment, and that the list has the minimum length.

## Constraints

- `0 <= len(a), len(b) <= 300`.
- Time `O(len(a) * len(b))`.

## Think about

The walk back from the corner of the table (chapter section 15) finds the operations from the **end** of the strings to the front. If you apply them in that same order (right to left), why do the positions of the characters you have not reached yet never move? What would go wrong if you reversed the list, as the chapter's `edit_script` does?
