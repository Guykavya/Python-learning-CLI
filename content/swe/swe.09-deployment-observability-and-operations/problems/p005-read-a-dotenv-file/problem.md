# Read a `.env` file

Chapter section 3.5 (`.env` files and secrets) and 3.4 (`--env-file`). A `.env` file holds `NAME=value` lines for local development. Write a small parser that follows the same simple rules as the files the chapter uses, and that **tells you the line number** when a line is wrong.

## What to write

```python
def parse_dotenv(text: str) -> dict[str, str]: ...
```

Rules, applied to each line (line numbers start at 1):

1. A line that is blank, or whose first non-space character is `#`, is skipped. There are **no inline comments**: `A=1 # note` has the value `1 # note`.
2. An optional leading `export ` is removed (`export NAME=value`).
3. The line is split at the **first** `=`. The name must match `[A-Za-z_][A-Za-z0-9_]*` (spaces around the name are removed). Anything else is an error.
4. The value has leading and trailing spaces removed. If it starts with `"` or `'`, it must end with the **same** quote (and be at least 2 characters long); the quotes are removed and the text inside is kept exactly, including `#`, `=` and spaces. A value that starts with a quote and does not end with it is an error.
5. Nothing else is interpreted: **no variable expansion** (`$HOME` stays `$HOME`) and no escape sequences (`\n` stays two characters).
6. `NAME=` gives the empty string. If a name appears twice, the last one wins.
7. Every error raises `ValueError` whose message contains `line N` (for example `line 3`).

## Example

```python
text = '''
# local settings
export APP_ENV=development
DATABASE_URL=postgresql://app:pw@db/app?sslmode=require
GREETING="hello world"   
PATH_NOTE='cost: $5 # not a comment'
EMPTY=
'''
parse_dotenv(text)
# {'APP_ENV': 'development',
#  'DATABASE_URL': 'postgresql://app:pw@db/app?sslmode=require',
#  'GREETING': 'hello world',
#  'PATH_NOTE': 'cost: $5 # not a comment',
#  'EMPTY': ''}

parse_dotenv("A=1\nthis is not a setting")   # ValueError: line 2: expected NAME=value
```
