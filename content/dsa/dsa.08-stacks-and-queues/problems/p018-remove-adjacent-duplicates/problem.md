# Remove adjacent duplicates

Repeatedly delete two **equal neighbouring** characters until no such pair is left: `"abbaca"` -> `"aaca"` -> `"ca"`. Write `remove_duplicates(s)` that returns a tuple `(result, pairs)`: the final string and how many pairs were deleted in total.

Do it in **one pass** with a stack (chapter section 7, "Remove adjacent duplicates"): if the new character equals the top of the stack, the two cancel (pop); otherwise push.

## Example

```python
>>> remove_duplicates("abbaca")
('ca', 2)
>>> remove_duplicates("azxxzy")
('ay', 2)
>>> remove_duplicates("aabb")
('', 2)
>>> remove_duplicates("aaa")
('a', 1)
>>> remove_duplicates("")
('', 0)
```

## Constraints

- `0 <= len(s) <= 10**5`. The last test has a time limit: repeatedly searching the string and rebuilding it is `O(n^2)`.

## Think about

The final result does not depend on which pair you delete first. Why does the stack, which always deletes the pair that appears at the top, still give the same answer?
