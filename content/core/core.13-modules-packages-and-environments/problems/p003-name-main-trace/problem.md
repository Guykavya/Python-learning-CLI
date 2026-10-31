# Trace: `__name__` when run or imported

Two files sit in the same folder:

```text
demo/
├── app.py
└── tools.py
```

`tools.py`:

```python
print("tools: __name__ is", __name__)


def shout(text):
    return text.upper() + "!"


if __name__ == "__main__":
    print("tools running as a script")
    print(shout("demo"))
```

`app.py`:

```python
print("app: __name__ is", __name__)
import tools

print(tools.shout("hi"))
print("tools.__name__ =", tools.__name__)

if __name__ == "__main__":
    print("app running as a script")
```

Inside `demo/` you run three commands, one after the other:

```bash
python app.py
python tools.py
python -c "import app"
```

Write the output of the first command, then a line `---`, then the output of the second command,
then a line `---`, then the output of the third command. Put it all in `answer.txt`.

**Example of the layout** (not the real answer):

```text
first command line 1
first command line 2
---
second command line 1
---
third command line 1
```
