## Approach

One pass over the instructions, then two checks that need the whole picture. The full code is `reference.py`; the key pieces:

```python
def _instructions(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        number, line = i + 1, lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        while line.endswith("\\") and i < len(lines):
            line = line[:-1].rstrip() + " " + lines[i].strip()
            i += 1
        keyword, _, rest = line.partition(" ")
        yield number, keyword.upper(), rest.strip()
```

Then, in `lint_dockerfile`, the `FROM` rule uses the last path component (`image.rsplit("/", 1)[-1]`) so that a registry port (`localhost:5000/app`) is not mistaken for a tag; `USER` is reset at every `FROM` because only the last stage ends up in the image; and `copy-before-install` compares line numbers after the walk.

## Complexity

O(number of lines). The real value is the habit: every mistake the chapter listed (cache order, PID 1, root, secrets, package lists) becomes one line of code you can run in CI.

## Another way

`hadolint` (a tool you run in Docker) knows over 70 rules and shells out to ShellCheck for the `RUN` lines. A regular expression per rule is shorter than this walk but cannot join continuation lines, track stages or compare the order of two instructions.
