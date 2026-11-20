# Longest common prefix

Write `longest_common_prefix(words)` that returns the longest string that every word in the list starts with (chapter section 7). An empty list gives `""`.

Solve it with a trie first: insert all words, then walk down from the root **while the path has no choice**. Then compare with a shorter way (see the solution).

## Example

```python
>>> longest_common_prefix(["flower", "flow", "flight"])
'fl'
>>> longest_common_prefix(["dog", "racecar", "car"])
''
>>> longest_common_prefix(["abc", "ab"])        # 'ab' is a whole word: the prefix cannot grow past it
'ab'
>>> longest_common_prefix(["same", "same"])
'same'
>>> longest_common_prefix([])
''
```

## Constraints

- Up to 10**4 words of up to 1000 characters each; any characters.
- `O(total length of the words)`.

## Think about

1. While walking down the trie, which **two** situations end the common prefix?
2. Why is `"ab"` the answer for `["abc", "ab"]`, although the node for `ab` has only one child?
3. What happens if one of the words is `""`?
