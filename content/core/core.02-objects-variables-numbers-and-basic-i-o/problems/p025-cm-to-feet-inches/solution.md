## Approach

Convert to the smallest unit you report (whole inches) and round there. Then split with `divmod`.
Rounding after splitting can produce `5 ft 12 in`.

## Code

```python
cm = float(input())
total_inches = round(cm / 2.54)
feet, inches = divmod(total_inches, 12)
print(f"{feet} ft {inches} in")
```

## Why round first

182.9 cm is 72.008 inches. Rounded first: 72 inches, which is `6 ft 0 in`.
If you split first you get 6 feet and 0.008 inches, which happens to be fine, but 182.8 cm is
71.97 inches: split first gives 5 feet and 11.97 inches, and rounding only the inches gives
`5 ft 12 in`, which is not a valid answer.

## Another way

`feet = total_inches // 12` and `inches = total_inches % 12` do the same as `divmod`.
