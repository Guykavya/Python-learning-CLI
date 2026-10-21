## Approach

Peel off the biggest unit first. Floor division gives how many whole units fit;
modulo gives what is left for the smaller units.

## Code

```python
total = int(input())
hours, rest = divmod(total, 3600)
minutes, seconds = divmod(rest, 60)
print(f"{hours}:{minutes:02d}:{seconds:02d}")
```

## Trace for 3661

- `divmod(3661, 3600)` gives `(1, 61)`
- `divmod(61, 60)` gives `(1, 1)`
- printed as `1:01:01`

## Another way

`minutes = total // 60 % 60` and `seconds = total % 60` work without `divmod`.
`divmod` is clearer because it states that both results belong together.
