## Hint 1

What is the cumulative AND of the flags of a session along the steps? (`df[steps].cumprod(axis=1)` does it for 0/1 values.) How would you recognise an inconsistent session with the plain flags and the cumulative ones?

## Hint 2

```text
flags = df[steps].astype(bool)
passed = flags.cummin(axis=1)         # True only while every flag so far is True
inconsistent = (flags & ~passed).any(axis=1).sum()
count at step = passed[step].sum()
```
