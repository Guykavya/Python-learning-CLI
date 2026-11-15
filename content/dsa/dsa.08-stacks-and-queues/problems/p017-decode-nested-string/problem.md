# Decode a nested string

A compressed string uses the rule `k[text]`: repeat `text` exactly `k` times. Groups can be nested and can stand next to plain letters. Write `decode(s)` that returns the expanded string (chapter section 7, "Decode a nested string").

- `k` is a positive integer and can have **several digits** (`12[a]`);
- letters outside any group are copied as they are;
- the input is always well formed.

## Example

```python
>>> decode("3[a]2[bc]")
'aaabcbc'
>>> decode("3[a2[c]]")
'accaccacc'
>>> decode("2[abc]3[cd]ef")
'abcabccdcdcdef'
>>> decode("10[x]")
'xxxxxxxxxx'
>>> decode("ab")
'ab'
```

`3[a2[c]]`: the inner `2[c]` is `cc`, so the group is `acc`, repeated 3 times.

## Constraints

- `1 <= len(s) <= 1000`; the decoded string has at most `10**6` characters.
- Letters are lower-case `a`-`z`.

## Think about

When you reach `[`, you are about to start a new, unfinished piece of text. What two things must you remember so that you can continue the outer piece when the matching `]` comes?
