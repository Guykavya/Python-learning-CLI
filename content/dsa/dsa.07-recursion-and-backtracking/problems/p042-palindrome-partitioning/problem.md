# Palindrome partitioning

Write `palindrome_partitions(s)` that returns every way to cut the string `s` into consecutive pieces so that **every piece is a palindrome**. Each way is a list of the pieces in order. The order of the ways does not matter (the tests sort).

For the empty string there is one way: no pieces, `[[]]`.

## Example

```python
>>> sorted(palindrome_partitions("aab"))
[['a', 'a', 'b'], ['aa', 'b']]
>>> palindrome_partitions("a")
[['a']]
```

## Constraints

- `0 <= len(s) <= 12`, lower-case letters.

## Think about

This is the "how long is the next piece" view (chapter section 13): from position `start`, the loop chooses where the next piece ends. Which pieces are allowed? When is a way complete?
