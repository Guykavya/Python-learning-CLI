# EAFP or LBYL?

Two styles of defensive code:

- **LBYL** ("look before you leap"): check first, then act. `if key in d: use d[key]`.
- **EAFP** ("it is easier to ask forgiveness than permission"): act, and handle the failure.
  `try: use d[key] except KeyError: ...`

Python prefers EAFP, or a built-in that already hides the check (`dict.get`, `setdefault`,
`getattr(obj, name, default)`). Reasons: the check often repeats the work (two lookups instead of
one), the world can change between the check and the use (a file deleted after `exists()`), and
a check can be **wrong**: `"-5".isdigit()` is `False`, yet `int("-5")` works.

`starter.py` has five LBYL functions. Copy it to `solution.py` and rewrite them. Keep names
and parameters.

- `get_port(config)`: `int(config["port"])`, default `8080`. **Touch the dict only once.**
- `add_word(index, word, line_no)`: append `line_no` to the list for `word`, creating the list
  when new. **One access** when the word already exists.
- `read_or_default(fs, path, default="")`: return the file text, or `default` if the file does
  not exist. Do **not** call `fs.exists`. Catch only `FileNotFoundError`; a `PermissionError` must
  still reach the caller.
- `display_name(obj)`: `obj.name.upper()`, or `"ANON"` if there is no `name`. Read `name` only once
  (it may be a property that does work).
- `parse_int(text)`: `int(text)`, or `None` when `text` is not a whole number. Unlike the
  starter, `"-5"`, `"+3"` and `" 7 "` are numbers.

The tests also check there is no `hasattr`, `.isdigit()`, `.exists()` call, and no `in` /
`not in` test inside `get_port` and `add_word`.

**Example**

```python
get_port({"port": "9000"})     # 9000
get_port({})                   # 8080
parse_int("-5")                # -5   (the starter returns None)
parse_int("4.2")               # None
```
