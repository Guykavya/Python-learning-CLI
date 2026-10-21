## Hint 1

Where exactly must the shebang go? What happens if there is a blank line or a
comment before it?

## Hint 2

`__file__` holds the path of the script, which may include folders.
`os.path.basename(path)` keeps only the last part.

## Hint 3

```
#!/usr/bin/env python3
import os

print("Running as:", __name__)
print("Script file:", os.path.basename(__file__))
```
