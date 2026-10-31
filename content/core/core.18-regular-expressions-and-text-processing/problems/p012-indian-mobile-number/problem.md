# Indian mobile number validator

Sign-up forms must accept the many ways people type a phone number, and reject the rest.
This is a classic job for one `re.fullmatch` pattern built from small optional pieces.

Write `is_mobile(s: str) -> bool` in `solution.py`. The rules:

1. Ignore spaces (and other whitespace) at the **start and end** of `s`.
2. An optional **prefix**, one of:
   - `+91`, optionally followed by **one** space or **one** hyphen, or
   - a single `0` written directly before the number (no space after it).
3. Then the **10-digit number**:
   - the first digit is `6`, `7`, `8` or `9`;
   - all ten are ASCII digits `0`–`9`;
   - there may be **one** space or **one** hyphen between the 5th and 6th digit, and nowhere else.
4. Nothing else is allowed (no `91` without `+`, no two prefixes, no brackets).

**Example**

```python
is_mobile("9876543210")         # True
is_mobile("+91 98765-43210")    # True
is_mobile("09876543210")        # True
is_mobile("  +919876543210 ")   # True   (outer spaces are ignored)
is_mobile("5876543210")         # False  (must start with 6-9)
is_mobile("9876 543210")        # False  (separator in the wrong place)
is_mobile("+91 09876543210")    # False  (two prefixes)
```
