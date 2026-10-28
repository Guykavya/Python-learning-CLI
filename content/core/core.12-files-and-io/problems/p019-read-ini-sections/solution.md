## Approach

`ConfigParser().read(path)` quietly ignores files that do not exist, so a missing file just leaves an empty parser, and `sections()` is `[]`. Build the dict with `dict(cp[section])`. `getint(section, option, fallback=...)` already handles a missing section or option. Keys are lower-cased by the parser, which the example shows.

## Code

```python
import configparser


def read_ini(path):
    cp = configparser.ConfigParser()
    cp.read(path, encoding="utf-8")
    return {section: dict(cp[section]) for section in cp.sections()}


def get_int(path, section, option, fallback):
    cp = configparser.ConfigParser()
    cp.read(path, encoding="utf-8")
    return cp.getint(section, option, fallback=fallback)
```

## Complexity

O(n) for the file size.

## Another way

`cp.read_string(text)` parses text you already have, which is handy in tests. For typed access there are also `getfloat` and `getboolean` (it understands `yes`, `on`, `true`, `1`).
