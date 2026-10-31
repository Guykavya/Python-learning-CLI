## Hint 1

When `list(m)` runs and `m` has no `__iter__`, Python calls `m[0]`, `m[1]` and so on by itself. How does it know when to stop? What must `__getitem__` do at the end so the loop stops instead of running forever?

## Hint 2

Check the index yourself: `if not isinstance(index, int): raise TypeError`, then `if not 0 <= index < self.count: raise IndexError(index)`. Rejecting negative numbers matters: with a negative index accepted, nothing would be wrong in a loop, but the tests (and `Multiples`) define the valid range as `0 .. count-1` exactly.

## Hint 3

```
Multiples.__getitem__(i): type check; range check; return step * (i + 1)
Backwards.__len__: return len(seq)
Backwards.__getitem__(i): type check; range check against len(seq); return seq[len(seq) - 1 - i]
```
Remember `reversed()` needs `__len__` and `__getitem__`; that is why `Multiples` (no `__len__`) cannot be reversed.
