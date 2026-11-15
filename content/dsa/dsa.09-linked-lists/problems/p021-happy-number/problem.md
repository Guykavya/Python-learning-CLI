# Happy number

Start with a positive integer and repeatedly replace it by the **sum of the squares of its digits**. If this reaches `1`, the number is **happy**. Otherwise the sequence falls into a loop that never contains `1`.

```text
19 -> 1² + 9² = 82 -> 8² + 2² = 68 -> 6² + 8² = 100 -> 1² + 0² + 0² = 1        happy
2  -> 4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 -> 20 -> 4 -> ...               not happy (back to 4)
```

Write `is_happy(n)` that returns `True` or `False`.

There is no list here, but the sequence **is** a linked list: each number's "next" is its digit-square sum (chapter section 7, "The same idea without any list"). Use fast and slow pointers on numbers, with `O(1)` extra memory: no set of seen numbers.

## Example

```python
>>> is_happy(19), is_happy(2), is_happy(1), is_happy(7)
(True, False, True, True)
```

## Constraints

- `1 <= n <= 2**31 - 1`.

## Think about

`1` leads to `1` again: it is a cycle of length one. So every sequence ends in a cycle; the question is only whether that cycle is `1`. Why can the sequence never grow forever? (Hint: how big is the digit-square sum of a number with 4 digits at most?)
