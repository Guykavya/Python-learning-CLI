# Palindrome check from both ends

Write `first_mismatch(text)`. Look only at the **letters and digits** of `text` (use `str.isalnum`), in **lower case**. Put them in a `deque` and compare the two ends: `popleft()` one character, `pop()` the other, and repeat while more than one character is left (chapter section 4, "Palindrome check from both sides").

- If every pair matches, the text is a palindrome: return `None`.
- Otherwise return the **first** pair that differs, as a tuple `(left_char, right_char)`.

## Example

```python
>>> first_mismatch("A man, a plan, a canal: Panama")
None
>>> first_mismatch("racecars")
('r', 's')
>>> first_mismatch("abcxba")
('c', 'x')
>>> first_mismatch("")
None
```

For `"abcxba"`: `a`/`a` match, `b`/`b` match, then `c`/`x` differ.

## Constraints

- `0 <= len(text) <= 10**5`.
- Odd length: the middle character has no partner and is never compared.

## Think about

Why does the loop condition `len(d) > 1` handle both even and odd lengths without a special case?
