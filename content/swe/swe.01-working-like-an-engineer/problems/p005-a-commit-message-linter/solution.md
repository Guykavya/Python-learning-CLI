## Approach

```python
def lint_message(msg):
    if not msg.strip():
        return ["empty"]
    lines = msg.rstrip().split("\n")
    problems = []
    if len(lines[0]) > 50:
        problems.append("subject-too-long")
    if lines[0].endswith("."):
        problems.append("subject-ends-with-period")
    if len(lines) > 1 and lines[1] != "":
        problems.append("no-blank-line")
    if any(len(line) > 72 for line in lines[1:]):
        problems.append("body-line-too-long")
    return problems
```

`rstrip()` removes the final newline that editors add, so a message that ends with `\n` has no phantom empty last line. Only the line directly after the subject has to be blank; later blank lines separate paragraphs and are normal.

Example: `"Add discount helper\nIt applies a percent."` has two lines and `lines[1]` is not empty, so the only problem is `no-blank-line`.

## Complexity

`O(length of the message)`.

## Another way

Many teams run exactly this check as a `commit-msg` git hook (chapter section 14), which refuses the commit when the list is not empty.
