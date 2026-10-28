# Compare two pip freeze outputs

`pip freeze` prints every installed package of an environment, one per line. It is a cheap lock file.
When an app works on Monday and breaks on Thursday, the first question is: **what changed in the
environment?** You will write the tool that answers it.

A freeze file can contain these lines:

```text
# pip freeze, Monday                    a comment: skip
Flask==3.0.0                            name==version
charset-normalizer==3.3.2
-e git+https://github.com/kavya/...      a line starting with "-" is an option: skip
mytool @ file:///home/kavya/mytool      name @ url (a direct reference)
                                        a blank line: skip
```

Write four functions in `solution.py`.

### `normalise(name)`

Package names are compared in the **PEP 503** normal form: lowercase, and every run of the
characters `-`, `_` and `.` becomes a single `-`. So `Flask`, `flask` are the same, and
`charset_normalizer`, `Charset.Normalizer` and `charset--normalizer` all become `charset-normalizer`.

### `parse_freeze(text)`

Return a dict: normalised name -> version string. For `name @ url` lines the "version" is the string
`"@ "` followed by the url. Strip spaces around names, versions and urls.
Raise `ValueError` if a line has another form (for example `requests>=2.0` or just `requests`), with
the line number (counting from 1) in the message, or if the same normalised name appears twice.

### `diff_freeze(old_text, new_text)`

Return a dict with five keys, each a list sorted by name:

- `"added"`: `(name, version)` only in new;
- `"removed"`: `(name, version)` only in old;
- `"upgraded"` / `"downgraded"`: `(name, old_version, new_version)` when both versions are made only
  of numbers and dots, compared as numbers part by part (`3.10` is newer than `3.9`);
- `"changed"`: `(name, old_version, new_version)` when the versions differ but cannot be compared
  that way (like `2.0rc1`, or urls).

Versions that are equal as numbers are **not** a change: `3.7` and `3.7.0` are the same version
(trailing `.0` parts do not matter).

### `format_diff(diff)`

Return the report as a list of lines, in this order: added (`+ name==version`), removed
(`- name==version`), upgraded (`^ name old -> new`), downgraded (`v name old -> new`), changed
(`~ name old -> new`). For a direct reference, added and removed lines use a space instead of `==`:
`+ mytool @ file:///...`. If nothing changed, return `["no changes"]`.

## Example

With the two files in `fixtures/` (`monday.txt` and `thursday.txt`):

```python
>>> d = diff_freeze(monday, thursday)
>>> d["upgraded"][:2]
[('certifi', '2024.2.2', '2024.7.4'), ('flask', '3.0.0', '3.0.3')]
>>> d["downgraded"]
[('urllib3', '2.2.0', '1.26.18')]
>>> for line in format_diff(d):
...     print(line)
+ markdown-it-py==3.0.0
+ rich==13.7.1
- colorama==0.4.6
^ certifi 2024.2.2 -> 2024.7.4
^ flask 3.0.0 -> 3.0.3
^ idna 3.6 -> 3.7.0
^ jinja2 3.1.2 -> 3.1.4
^ requests 2.31.0 -> 2.32.3
v urllib3 2.2.0 -> 1.26.18
~ mytool @ file:///home/kavya/mytool -> @ file:///home/kavya/mytool-v2
```

`charset-normalizer` is not in the report: only the spelling of its name changed. The editable
`-e` line is skipped.
