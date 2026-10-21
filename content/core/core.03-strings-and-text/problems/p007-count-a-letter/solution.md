## Approach

`count()` counts non-overlapping occurrences. It is case-sensitive, so for the second line convert **both** strings with `casefold()` before counting.

## Code

```python
text = input()
letter = input()
print(f"Exact: {text.count(letter)}")
print(f"Any case: {text.casefold().count(letter.casefold())}")
```

## Why both sides

If you casefold only the text, an uppercase letter like `B` will never be found in the now-lowercase text.

## Another way

`lower()` works for most English text. `casefold()` is the tool designed for this job and handles more languages.
