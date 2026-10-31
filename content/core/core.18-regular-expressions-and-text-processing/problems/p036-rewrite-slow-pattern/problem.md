# Rewrite a slow pattern

A form checks that a "title" is made of words separated by single whitespace characters. Its
author wrote:

```python
SLOW_RE = re.compile(r"(\w+\s?)*")

def is_title(s):
    return SLOW_RE.fullmatch(s) is not None
```

It gives the right answers, but `is_title("a" * 30 + "!")` takes minutes: `\w+` repeated by
`*` can split a run of letters in exponentially many ways, and the `!` forces the engine to try
all of them before it can say no.

Your job: in `solution.py`, define a module-level compiled pattern `SAFE_RE` such that

- `SAFE_RE.fullmatch(s)` succeeds for **exactly** the same strings as `SLOW_RE.fullmatch(s)`;
- it is fast on every input, including near-misses like `"a" * 30 + "!"`
  (the tests allow 0.5 seconds; a good answer needs well under a millisecond).

**Do not run `SLOW_RE` on long near-miss strings while experimenting.** Stay below about 20
letters, or your terminal will hang.

First work out which strings `SLOW_RE` accepts. A few to start you off:

| `s` | accepted? |
|---|---|
| `""` | yes (zero repetitions) |
| `"hello"` | yes |
| `"hello world"` | yes |
| `"hello world "` | yes (one trailing whitespace character) |
| `"hello  world"` | no (two spaces in a row) |
| `" hello"` | no (cannot start with a space) |
| `"hi!"` | no (`!` is not a word character) |

**Example**

```python
SAFE_RE.fullmatch("one two\tthree") is not None   # True
SAFE_RE.fullmatch("one  two") is not None         # False
SAFE_RE.fullmatch("a" * 30 + "!")                 # None, instantly
```
