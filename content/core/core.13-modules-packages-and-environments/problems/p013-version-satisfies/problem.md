# Does a version satisfy a specifier?

A requirement like `requests>=2.31,<3` means "any version from 2.31 up to, but not including, 3".
pip checks every candidate version against such a **specifier**. Here you write a small version of
that check.

Write `satisfies(version, spec)` in `solution.py`. It returns `True` or `False`.

- `version` is a dotted number like `"1.10.2"`. Only digits and dots.
- `spec` is a list of **clauses** separated by commas, like `">=1.2,<2.0"`. Spaces around clauses and
  operators are allowed (`">= 1.2 , < 2.0"`). The empty spec `""` allows every version.
- Each clause is an operator followed by a version. The operators are `==`, `!=`, `>=`, `<=`, `>`, `<`.
- The version must satisfy **all** clauses.
- Compare versions as **tuples of integers**, not as strings: `"1.10"` is newer than `"1.9"`.
  Pad the shorter tuple with zeros, so `"1.2"` and `"1.2.0"` are equal.
- A clause with any other operator (for example `~=1.0` or `=1.0`) raises `ValueError`.

**Example**

```python
satisfies("1.10", ">=1.9")            # True    (as strings, "1.10" < "1.9"!)
satisfies("2.0", ">=1.2,<2.0")        # False   (2.0 is not < 2.0)
satisfies("1.2", "==1.2.0")           # True    (padded with zeros)
satisfies("3.0.1", " != 3.0.1 ")      # False
satisfies("0.1", "")                  # True
satisfies("1.0", "~=1.0")             # ValueError
```
