## Code

```python
code = input()
print(code.zfill(6))
print(code.rjust(8, "."))
print(code.ljust(8, ".") + "|")
```

## Notes

- `zfill` knows about signs: it puts zeros after a leading `+` or `-`.
- `rjust(8, ".")` puts the text on the right and fills the left. The names describe where the **text** goes, not the padding.
- None of these methods cut a long string.

## Another way

f-strings do the same: `f"{code:.>8}"` and `f"{code:.<8}|"`. For a string, `f"{code:0>6}"` pads with zeros but does not move the sign, so `zfill` is the right tool for line 1.
