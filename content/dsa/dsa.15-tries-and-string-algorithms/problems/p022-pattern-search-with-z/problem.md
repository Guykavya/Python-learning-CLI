# Pattern search with Z

A DNA tool needs, for every position of a long read, how far the reference pattern matches from there. Write two functions using the Z-function (chapter section 12):

- `match_lengths(text, pattern)`: a list of `len(text)` numbers; entry `i` is the length of the longest common prefix of `pattern` and `text[i:]` (at most `len(pattern)`);
- `z_search(text, pattern)`: the sorted start positions of all (overlapping) occurrences of `pattern` in `text`. The empty pattern occurs at every position `0..len(text)`.

The strings may contain **any** characters, so there is no safe separator character. Make the Z-function work **without** one.

## Example

```python
>>> match_lengths("abaab", "aba")
[3, 0, 1, 2, 0]
>>> z_search("abababab", "abab")
[0, 2, 4]
>>> z_search("a#a#a", "#a")              # '#' is an ordinary character here
[1, 3]
>>> match_lengths("xyz", "")
[0, 0, 0]
```

## Constraints

- `len(text) <= 5 * 10**5`, `len(pattern) <= 10**5`; any characters.
- `O(len(text) + len(pattern))`.

## Think about

1. Compute `z` of `pattern + text` with **no** separator. For a text position `i`, can `z[len(pattern) + i]` be larger than `len(pattern)`? What does the extra part mean, and why is `min(z, m)` still the right answer?
2. Can a match that starts in the text ever "borrow" characters from the pattern part? Why not?
3. How does `z_search` follow from `match_lengths`?
