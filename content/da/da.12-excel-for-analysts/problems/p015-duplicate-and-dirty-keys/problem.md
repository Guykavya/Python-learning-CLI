# Duplicate and dirty keys

Chapter section 7.3. A lookup silently uses the **first** match, and a key with a trailing space or another case may not match at all. Before writing any lookup, **audit the key column**.

Write `key_report(keys)` for a list of keys (strings, numbers or `None`). Normalise a key as `str(key).strip().upper()`; ignore `None` and empty text. Return a dict with:

| key | value |
|---|---|
| `duplicates` | sorted list of **normalised** keys that occur more than once |
| `with_spaces` | sorted list of the **original** strings that have a leading or trailing space |
| `case_variants` | sorted list of normalised keys that appear with **more than one spelling of the case** among the stripped originals (`"p05"` and `"P05"`) |
| `numbers_as_text` | sorted list of the original strings that consist only of digits after stripping (`"105"`, `" 7 "`); real numbers are **not** listed |

Each list has no repeated entries.

## Example

`key_report(["P05", "p05", "P06 ", "P07", "P07", "105", 105, None])` gives `duplicates = ["105", "P05", "P07"]`, `with_spaces = ["P06 "]`, `case_variants = ["P05"]` and `numbers_as_text = ["105"]`.
