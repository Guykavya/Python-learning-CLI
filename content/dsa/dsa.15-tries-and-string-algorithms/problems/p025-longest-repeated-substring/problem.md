# Longest repeated substring

A plagiarism checker looks for the longest passage that appears twice in a document. Write `longest_repeat(s)` that returns a longest substring that occurs **at least twice** in `s` (the two occurrences may overlap). Return `""` if no character repeats. Use prefix hashes and binary search on the length (chapter section 14).

## Example

```python
>>> longest_repeat("banana")          # at 1 and 3, overlapping
'ana'
>>> longest_repeat("abcd")
''
>>> longest_repeat("aaaaa")
'aaaa'
>>> len(longest_repeat("mississippi"))   # 'issi' at 1 and 4
4
```

When several substrings have the longest length, any one of them is accepted: the tests check that yours occurs twice and has the right length.

## Constraints

- `0 <= len(s) <= 10**5`; any characters.
- Expected `O(n log n)`. Putting all substrings of every length into sets is `O(n**2)` substrings.

## Think about

1. If some substring of length `L` occurs twice, why does some substring of length `L - 1` occur twice as well? What does that allow?
2. How do you test one length `L` in `O(n)`, using the hash of every window of length `L`?
3. A hash collision could make the test say "yes" wrongly. How do you make sure the answer you return is a real repeat?
