# Practical against statistical

Chapter section 6.2. "Statistically significant" (the interval excludes 0) and "worth acting on" (the interval lies above the minimum
effect of interest, MEI) are different questions. Write `classify(lo, hi, mei=0.5)` returning a tuple `(label, significant)`:

- `label` is exactly one of the three strings of the chapter's `verdict`:
  `"worth it: the whole interval is above the minimum effect"` (when `lo > mei`),
  `"not worth it: the whole interval is below the minimum effect"` (when `hi < mei`),
  `"inconclusive: the interval contains the minimum effect"` (otherwise);
- `significant` is `True` when the interval **excludes zero** (`lo > 0` or `hi < 0`), else `False`.

```python
classify(0.06, 0.14)       # ("not worth it: ...", True): significant and not worth it
classify(-1.53, 4.53)      # ("inconclusive: ...", False)
classify(0.14, 2.86)       # ("inconclusive: ...", True)
```

## Example

The first example is the surprising row of the chapter: a highly significant effect that is far too small to matter.
