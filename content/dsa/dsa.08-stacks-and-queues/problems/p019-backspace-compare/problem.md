# Compare strings with backspaces

In these strings, `#` is a **backspace**: it deletes the character typed before it (if there is one). `"ab#c"` types as `"ac"`; `"a##c"` types as `"c"`; a `#` on an empty line does nothing.

Write two functions:

1. `type_text(s)`: return the text that `s` produces. Use a list as a stack (chapter section 7, "Compare strings with backspaces").
2. `backspace_equal(a, b)`: return `True` if `a` and `b` produce the same text, using only **`O(1)` extra memory**: do not build the typed strings or any list. Walk both strings from the **end** with two indices, counting the backspaces you still have to apply.

The tests measure the memory that `backspace_equal` allocates on two strings of 1,000,000 characters (with `tracemalloc`). A version that calls `type_text` allocates several megabytes and fails that one test; the other tests check correctness.

## Example

```python
>>> type_text("ab#c"), type_text("a##c"), type_text("#a#")
('ac', 'c', '')
>>> backspace_equal("ab#c", "ad#c")
True
>>> backspace_equal("a#c", "b")
False
>>> backspace_equal("a##c", "#a#c")
True
```

## Constraints

- `0 <= len(a), len(b) <= 10**6`; the strings contain lower-case letters and `#`.

## Think about

Reading from the end, when you see a `#` you know the **next** letter you meet (going left) is deleted. Why is the end the right place to start, and not the beginning?
