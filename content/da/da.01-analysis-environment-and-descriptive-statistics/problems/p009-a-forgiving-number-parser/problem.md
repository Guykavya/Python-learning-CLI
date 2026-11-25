# A forgiving number parser

Chapter section 7.4. Real CSV columns hold `"1,204"`, `" 98ms "`, `"$ 12.50"`, `"N/A"`. Write `parse_number(text)` that turns one cell into a `float`, following exactly these rules, in this order:

1. Strip whitespace and lower-case the text.
2. If the result is one of `""`, `"na"`, `"n/a"`, `"nan"`, `"null"`, `"none"`, `"-"`, `"?"`: return `None` (**missing**, not an error).
3. Remove these junk pieces, in this order: `"rs."`, `"rs"`, `"ms"`, `"%"`, `"$"`; then remove every comma and every space inside the text.
4. Convert with `float`. Scientific notation (`"1e3"`) works for free.
5. If `float` fails, **or** the result is not finite (`inf`, `nan`), raise `ValueError` whose message contains the original text.

## Example

```python
parse_number("1,204")      # 1204.0
parse_number(" 98ms ")     # 98.0
parse_number("Rs. 500")    # 500.0
parse_number("N/A")        # None
parse_number("abc")        # ValueError: cannot parse 'abc'
```
