# A small `.gitignore` matcher

Write `is_ignored(path, patterns)`: would git ignore `path`, given the lines of a `.gitignore` file?

`path` is relative to the repository root and uses `/`. A path that **ends with `/`** is a directory; any other path is a file.

## The rules you must support (a teaching subset of the real ones)

1. Blank lines and lines starting with `#` are ignored. Surrounding spaces of a line are ignored.
2. `*` matches any characters except `/`. `?` matches one character except `/`.
3. A pattern **without** a `/` (not counting a trailing one) matches the **name** of a file or folder at any depth: `*.pyc` matches `a.pyc` and `src/pkg/a.pyc`.
4. A pattern with a `/` at the start or in the middle is **anchored** to the root: `/todo.txt` matches only `todo.txt`; `docs/*.md` matches `docs/a.md` but not `x/docs/a.md`.
5. A **trailing `/`** means "directories only": `build/` ignores the folder `build` (and everything inside it), but not a file called `build`.
6. `**/` at the start matches in any directory (`**/cache/`); `/**` at the end matches everything inside; `a/**/b` matches `a/b`, `a/x/b`, `a/x/y/b`.
7. A leading `!` **re-includes** what an earlier pattern ignored. The **last** matching pattern wins.
8. If a **parent directory** is ignored, everything inside it is ignored, and a `!` rule cannot bring a file back (git: "it is not possible to re-include a file if a parent directory is excluded").

## Example

```python
pats = ["*.pyc", "__pycache__/", "build/", "!keep.pyc"]
is_ignored("src/a.pyc", pats)            # True
is_ignored("keep.pyc", pats)             # False
is_ignored("__pycache__/", pats)         # True: a directory
is_ignored("__pycache__", pats)          # False: a FILE with that name
is_ignored("docs/build/index.html", pats)  # True: inside an ignored directory
```

Anything else of the real format (character classes `[abc]`, escapes, `.git/info/exclude`) is out of scope. One test (skipped when git is missing) compares 10 of the cases with `git check-ignore`.
