# Trace: a module runs only once

Two files sit in the same folder:

```text
demo/
├── counter.py
└── main.py
```

`counter.py`:

```python
print("loading counter")
count = 0


def add():
    global count
    count += 1
    return count
```

`main.py`:

```python
import sys
import importlib

print("start")
import counter
print(counter.add())
import counter
print(counter.add())
print("counter" in sys.modules)
same = sys.modules["counter"] is counter
print(same)
old = counter
counter = importlib.reload(counter)
print(counter.count)
print(counter is old)
print(counter.add())
```

You run `python main.py` inside `demo/`.

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
The program never stops with an error.
