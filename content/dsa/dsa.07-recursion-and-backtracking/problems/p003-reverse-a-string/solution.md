## Approach

The first character of `s` becomes the last character of the result. Reverse the rest and append the first character. The empty string is its own reverse.

## Code

```python
def reverse(s):
    if s == "":
        return ""
    return reverse(s[1:]) + s[0]
```

## Complexity

`O(n^2)` time, because each call copies the rest of the string (`s[1:]`) and builds a new result string. `O(n)` stack depth.

## Another way

Use an index and swap from both ends in a list of characters:

```python
def reverse(s):
    chars = list(s)

    def go(lo, hi):
        if lo >= hi:
            return
        chars[lo], chars[hi] = chars[hi], chars[lo]
        go(lo + 1, hi - 1)

    go(0, len(chars) - 1)
    return "".join(chars)
```

This version has depth `n / 2` and `O(n)` time. In real code `s[::-1]` is the answer.
