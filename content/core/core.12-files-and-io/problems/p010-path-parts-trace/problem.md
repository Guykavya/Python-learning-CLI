# Trace: names, stems and suffixes of a path

These are pure path operations: no file on disk is needed. We use `PurePosixPath`, so output uses `/` on every system. Predict each line.

```python
from pathlib import PurePosixPath as P

p = P("data/reports/sales.2024.csv")
print(p.name)
print(p.stem)
print(p.suffix)
print(p.suffixes)
print(p.parent)
print(p.parent.name)
print(p.with_suffix(".json"))
print(p.with_name("totals.txt"))
print(p.with_stem("q1"))
print(p.parts)
print(P("a") / "b" / "c.txt")
print(P("a/b") / "/etc")
print(P("x.tar.gz").suffix)
print(P("noext").suffix == "")
print(P("a/../b").parts)
print((P("/") / "x").is_absolute())
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`. A print of an empty string is an empty line. The program never stops with an error, so you never need to write a traceback.
