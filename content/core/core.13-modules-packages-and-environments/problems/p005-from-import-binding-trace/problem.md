# Trace: `from`-import copies the name, not the variable

`from settings import level` makes a **new name** `level` in your file that points to the same object
as `settings.level` at that moment. Trace what happens when either side changes later.

```text
demo/
├── settings.py
└── main.py
```

`settings.py`:

```python
level = 1
names = ["ann"]


def bump():
    global level
    level += 1
    return level
```

`main.py`:

```python
from settings import level, names, bump
import settings

print(level, settings.level)
bump()
print(level, settings.level)
settings.level = 10
print(level, settings.level)
level = 99
print(level, settings.level)
names.append("ben")
print(settings.names)
settings.names = ["cat"]
print(names, settings.names)
from settings import level
print(level)
print(bump(), level)
```

You run `python main.py` inside `demo/`. Write exactly what it prints, one line for each printed line,
in `answer.txt`. The program never stops with an error.
