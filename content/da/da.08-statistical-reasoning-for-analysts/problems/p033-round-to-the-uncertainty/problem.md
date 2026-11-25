# Round to the uncertainty

Chapter section 9.1. Printing `2577.612` for a mean whose standard error is 63 rupees claims a precision the data do not have. Round a
value to the precision of its **uncertainty** `ref` (usually the standard error): about two significant digits of `ref`.

Write `sig_round(value, ref)` returning a **string**:

- `decimals = max(0, 1 - floor(log10(abs(ref))))`: SE 63 gives 0 decimals, SE 5.9 gives 1, SE 0.4 gives 2;
- round `value` to that many decimals and format it with a thousands separator and exactly that many decimals (`f"{x:,.{decimals}f}"`);
- when `ref` is 0 or not finite (`nan`, `inf`), return the value as a whole number with the separator (`f"{value:,.0f}"`).

```python
sig_round(2577.616, 63)       # '2,578'
sig_round(2498.13, 5.9)       # '2,498.1'
sig_round(12.3456, 0.4)       # '12.35'
```

## Example

`sig_round(1234567.891, 120)` is `'1,234,568'`: with a standard error of 120, the digits after the point mean nothing.
