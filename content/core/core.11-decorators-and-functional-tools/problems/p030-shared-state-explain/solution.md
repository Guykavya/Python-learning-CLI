## Approach

Count the copies. One global variable means one shared number. A variable created inside the
decorator body is created again every time the decorator is applied, so each wrapper gets its
own through its closure.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Run this in the REPL after the fix: `add.__closure__[0].cell_contents` shows the value captured
for `add`, and `mul.__closure__[0].cell_contents` shows a different cell. Seeing two cells makes
"one counter per function" concrete. (The order of the cells can differ; look for the number.)
