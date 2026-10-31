## Approach

Keep two ideas apart. **Finding and running** a module happens once per program; **binding a name**
happens on every `import` line. The cache that makes this work is `sys.modules`. The `__name__` variable
tells a file whether it is the started program or an imported module.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Prove it yourself: add `import sys` and `print("temps" in sys.modules)` before and after the first
import in `report.py`. Then add `print(__name__)` at the top of `temps.py` and run both files.
