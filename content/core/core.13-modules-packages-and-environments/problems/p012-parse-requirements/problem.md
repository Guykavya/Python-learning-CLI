# Parse a `requirements.txt` file

`pip install -r requirements.txt` reads a list of packages, one per line, each with an optional
**version specifier** like `==3.0.2` or `>=2.31,<3`. Before you upgrade or audit a project, you often
want that list as data.

Write `parse_requirements(path)` in `solution.py`. It reads the file (UTF-8) and returns a list of
`(name, specifier)` tuples, in file order.

Rules for each line:

1. A `#` starts a comment. Drop it and everything after it.
2. Strip spaces. Skip lines that are now empty.
3. Skip **option lines**: lines that start with `-` (like `-r other.txt` or `--index-url ...`).
4. An **environment marker** starts at `;` (like `; python_version >= "3.10"`). Drop it and everything after it.
5. The **name** is the first run of characters that are letters, digits, `-`, `_` or `.`.
   Normalise it the way pip compares names: lowercase, and every `_` and `.` becomes `-`.
6. **Extras** in square brackets right after the name (like `uvicorn[standard]`) are dropped.
7. The **specifier** is the rest of the line with **all** spaces removed. It is `""` when there is none.

**Example** (`requirements.txt`)

```text
# app dependencies
requests>=2.31,<3   # http client
Flask==3.0.2
python_dateutil
numpy >= 1.26 ; python_version >= "3.10"
uvicorn[standard]~=0.29

-r dev-requirements.txt
--index-url https://example.org/simple
Django.Rest_Framework!=3.14.0
```

```python
parse_requirements("requirements.txt")
# [('requests', '>=2.31,<3'),
#  ('flask', '==3.0.2'),
#  ('python-dateutil', ''),
#  ('numpy', '>=1.26'),
#  ('uvicorn', '~=0.29'),
#  ('django-rest-framework', '!=3.14.0')]
```

This file is also in `fixtures/requirements.txt`.
