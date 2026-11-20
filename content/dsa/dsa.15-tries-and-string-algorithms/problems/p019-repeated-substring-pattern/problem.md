# Repeated substring pattern

A compression tool stores a string as "block times count" when it is one block repeated. Write `repeat_info(s)` that returns `(block, count)` with the **shortest** block such that `block * count == s`. If `s` is not made of a smaller block repeated two or more times, return `(s, 1)`.

## Example

```python
>>> repeat_info("abcabcabc")
('abc', 3)
>>> repeat_info("aaaa")
('a', 4)
>>> repeat_info("abcab")          # period 3, but 3 does not divide 5
('abcab', 1)
>>> repeat_info("z")
('z', 1)
```

## Constraints

- `1 <= len(s) <= 10**6`; any characters.
- `O(n)` (chapter section 11, "Is `s` a repeated block?").

## Think about

1. Why is the shortest block, if there is one, exactly the smallest period `p = n - pi[n - 1]`?
2. Why must `p` divide `n`? Give a string with a smallest period that does not divide its length.
3. Could a longer block that divides `n` exist when the smallest period does not divide `n`?
