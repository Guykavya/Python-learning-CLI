# Near duplicates

Chapter section 5.5. Sometimes no clean key exists: `John Smith` and `Jon  Smith` are probably one person. The standard
library's `difflib.SequenceMatcher(None, a, b).ratio()` gives a similarity between 0 and 1 (1 means identical). It is
slow, because every pair is compared, but it needs nothing else. Fuzzy matching should **suggest**, not decide: your
function lists the suspicious pairs, a person looks at them.

Write `similar_names(names, threshold=0.85)`:

- `names` is a list of text.
- **Normalise** each name before comparing: lower case, and any run of white space (spaces, tabs) becomes **one space**,
  with no space at the ends (`" ".join(name.lower().split())`).
- Compare every pair `(i, j)` with `i < j` using `SequenceMatcher(None, keys[i], keys[j]).ratio()` on the normalised
  names, in that order (the earlier name first). A name is never compared with itself.
- Return a **sorted list of tuples `(i, j)`** (positions in `names`, `i < j`) of the pairs whose ratio is **at least**
  `threshold` (greater than or equal).
- Two different positions with the same normalised name are a pair with ratio 1.0.
- Do not change `names`. The list can hold 300 names, so a plain double loop must be fast enough (about a second).

## Example

```python
names = ["John Smith", "Jon  Smith", "Joan Smythe", "Priya Nair", "Priya Nayar", "john smith"]
print(similar_names(names))
print(similar_names(names, threshold=0.8))
print(similar_names(names, threshold=1.0))
```

```text
[(0, 1), (0, 5), (1, 5), (3, 4)]
[(0, 1), (0, 5), (1, 2), (1, 5), (3, 4)]
[(0, 5)]
```

Hand check for `(3, 4)`: `priya nair` (10 letters) and `priya nayar` (11) share `priya na` (8) and the final `r` (1),
so 9 matching characters and a ratio of `2 * 9 / 21 = 0.857`. The pair `(1, 2)` has ratio exactly `2 * 8 / 20 = 0.8`: it
appears only when the threshold is 0.8, because "at least" includes the limit.
