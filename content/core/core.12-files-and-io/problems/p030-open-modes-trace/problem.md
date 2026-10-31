# Trace: what do the modes really do?

Mode `"w"` truncates, `"a"` appends, `"x"` refuses to touch an existing file, and `"r"` cannot write.
Predict every line. Pay attention to **when** the size of the file changes.

```python
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "log.txt"

    with open(path, "w", newline="\n") as f:
        f.write("one\ntwo\n")
    print(path.read_text().splitlines())

    with open(path, "a", newline="\n") as f:
        f.write("three\n")
        print(f.tell())
    print(path.read_text().splitlines())

    with open(path, "w", newline="\n") as f:
        print(path.stat().st_size)
        f.write("new\n")
        print(path.stat().st_size)
    print(path.stat().st_size)
    print(path.read_text().splitlines())

    try:
        with open(path, "x") as f:
            f.write("never\n")
    except FileExistsError:
        print("exists")

    with open(path, "r", newline="\n") as f:
        try:
            f.write("oops")
        except Exception as error:
            print(type(error).__name__)
        print(f.read().splitlines())
        print(f.read() == "")
```

`newline="\n"` only makes the bytes the same on every system. You can ignore it.

Write exactly what the program prints to **standard output**, one line for each printed line, in `answer.txt`.
The program never ends with a traceback. Lines sent to `sys.stderr` do not count.
