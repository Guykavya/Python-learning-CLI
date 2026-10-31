## Approach

A traceback prints frames outermost first, so the innermost frame of one traceback is its last
frame line. A chain prints the older exception first and the newest one last. Put together:
**the innermost frame of the last traceback is simply the last frame line in the whole text.**
No need to split the text into blocks.

The only care needed is to recognise frame lines correctly:

- anchor at the start of a line (`re.MULTILINE`) and require exactly two spaces, so indented
  source lines such as `    print('File "x"')` never match;
- make `, in <function>` optional for `SyntaxError` tracebacks;
- convert the line number with `int`.

## Code

```python
import re

FRAME_RE = re.compile(r'^  File "(.+?)", line (\d+)(?:, in (.+))?$', re.MULTILINE)


def blame(tb_text: str) -> tuple[str, int, str]:
    """(file, line, function) of the innermost frame of the last traceback."""
    frames = FRAME_RE.findall(tb_text)
    if not frames:
        raise ValueError("no frame lines in this text")
    file, line, function = frames[-1]
    return file, int(line), function
```

With three groups `findall` returns tuples of three strings. A group that did not take part
(no `, in ...`) comes back as `""`, which is exactly what the task asks for.

`$` with `re.MULTILINE` matches before a `\n`. Text copied from Windows can have `\r\n` line
ends; `(.+)` would then keep the `\r`. `str.splitlines()` (below) handles both.

## Complexity

O(n) in the length of the text: one regex scan.

## Another way

Loop over the lines from the end and stop at the first frame line:

```python
def blame(tb_text):
    for line in reversed(tb_text.splitlines()):
        if line.startswith('  File "'):
            m = re.match(r'  File "(.+?)", line (\d+)(?:, in (.+))?$', line)
            if m:
                return m[1], int(m[2]), m[3] or ""
    raise ValueError("no frame lines in this text")
```

This stops early and copes with `\r\n` because `splitlines` removes it.

When you have the exception object (not the text), do not parse at all:
`traceback.extract_tb(exc.__traceback__)[-1]` gives a `FrameSummary` with `.filename`,
`.lineno` and `.name`.
