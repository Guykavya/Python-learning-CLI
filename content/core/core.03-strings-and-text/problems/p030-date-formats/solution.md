## Code

```python
y, m, d = input().strip().split("-")
y, m, d = int(y), int(m), int(d)
months = "JanFebMarAprMayJunJulAugSepOctNovDec"
print(f"{d:02}/{m:02}/{y}")
print(f"{d} {months[3 * (m - 1):3 * m]} {y}")
print(f"{y}{m:02}{d:02}")
```

## Why convert to int

`int("05")` is 5, which gives "no leading zero" for free. The `02` spec puts the zero back where it is wanted. Converting also checks that the parts really are numbers.

## Another way

The `datetime` module (core.12) parses and formats dates properly: `date.fromisoformat(s)` and `f"{d:%d/%m/%Y}"`. It also rejects impossible dates like February 30. The slicing trick here is for practice.
