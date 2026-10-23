## Approach

Turn the text to lower case once, so there are five letters to look for instead of ten. Loop over the characters and count those found in `"aeiou"`. The empty string needs no special case: the loop does nothing and the counter stays 0.

## Code

```python
def count_vowels(text):
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count
```

## Complexity

O(n) time for n characters, O(1) extra space.

## Another way

`sum(1 for ch in text.lower() if ch in "aeiou")` is shorter. The loop is easier to debug with `print`.
