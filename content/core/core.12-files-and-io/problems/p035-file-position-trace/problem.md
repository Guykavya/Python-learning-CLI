# Trace: positions, r+ and a, and a with block that fails

A file object has a **position**. `read`, `write`, `readline`, `seek` and `tell` all work with it.
Mode `"r+"` can read and write. Mode `"a"` always writes at the end, whatever the position says.
A `with` block closes the file even when an error happens inside it.

Predict the exact output. The program uses `write_bytes` and `newline=""` so that line endings are the same on
every system, and all the text is plain ASCII, so a position in characters is a position in bytes.

```python
import sys
import tempfile
from pathlib import Path


def show(label, value):
    print(f"{label}: {value!r}")


with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "data.txt"
    path.write_bytes(b"abcdef\nghij\n")

    with open(path, "r+", newline="") as f:
        show("start", f.tell())
        show("read", f.read(3))
        show("tell", f.tell())
        f.seek(0, 2)
        show("end", f.tell())
        f.write("klm\n")
        show("after write", f.tell())
        f.seek(0)
        show("line", f.readline())
        show("tell", f.tell())
        f.seek(2)
        f.write("XY")
        f.seek(0)
        show("all", f.read())
        show("eof", f.read())

    with open(path, "a", newline="") as f:
        show("append start", f.tell())
        f.seek(0)
        f.write("Z\n")
        show("append tell", f.tell())

    try:
        with open(path, "a", newline="") as f:
            f.write("before\n")
            show("inside", f.closed)
            raise ValueError("boom")
            f.write("never\n")
    except ValueError as error:
        show("caught", str(error))
        show("closed", f.closed)
        print("problem found", file=sys.stderr)

    show("lines", path.read_bytes().decode().splitlines())
    show("size", path.stat().st_size)
```

Write exactly what the program prints to **standard output**, one line for each printed line, in `answer.txt`.
The program never ends with a traceback. Lines sent to `sys.stderr` do not count.

`show` prints the label, a colon, a space, and the `repr` of the value (strings have quotes and `\n`).
