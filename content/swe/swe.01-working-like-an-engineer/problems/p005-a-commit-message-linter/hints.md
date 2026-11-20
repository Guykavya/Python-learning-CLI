## Hint 1

Split the message into lines. Which line is the subject? Which lines are the body, and what must the line between them be?

## Hint 2

After `msg.rstrip()` an empty result means `"empty"`. Then `lines = msg.rstrip().split("\n")`; `lines[0]` is the subject; `lines[1:]` is everything after it.

## Hint 3

```text
if not msg.strip(): return ["empty"]
lines = msg.rstrip().split("\n")
problems = []
if len(lines[0]) > 50: add "subject-too-long"
if lines[0].endswith("."): add "subject-ends-with-period"
if len(lines) > 1 and lines[1] != "": add "no-blank-line"
if any(len(l) > 72 for l in lines[1:]): add "body-line-too-long"
```
