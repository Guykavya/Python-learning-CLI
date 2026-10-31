# A word-frequency tool that reads stdin

Unix tools read from **standard input** when you give no file, so you can write `cat book.txt | wordfreq`.
Write `main(argv=None)` in `solution.py`. It returns an exit code (it does not call `sys.exit`).

**Arguments** (use `argparse`)

- `files`: zero or more paths. With no path (or with the path `-`), read `sys.stdin`.
- `-n N` / `--top N`: show only the `N` most common words. `N` is an `int`, default `10`, and must be at least 1.
  A bad value (`-n abc`, `-n 0`) makes the parser print an error and exit with code 2. Use `parser.error(...)` for the
  `0` case.
- `--min K`: ignore words that occur fewer than `K` times. `int`, default `1`.

**Words.** Lower-case the text. A word is a run of letters (`str.isalpha()`) and apostrophes `'`. Everything else
separates words. Read the input **line by line** (never `read()` everything).
Count words over **all** the inputs together.

**Output.** One line per word, `word count`, sorted by count (highest first), then by word (A to Z). Return `0`.

**Errors.** A file that does not exist: print `error: cannot read <path>` to **stderr**, print nothing to stdout, and
return `2`. If there are no words at all (after `--min`), print `no words` to **stderr** and return `1`.

**Example**

```text
$ printf "The cat and the hat.\nThe end" | wordfreq -n 2
the 3
and 1
```
