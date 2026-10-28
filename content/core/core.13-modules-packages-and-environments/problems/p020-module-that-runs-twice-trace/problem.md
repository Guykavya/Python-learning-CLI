# Trace: the module that runs twice

A module is cached in `sys.modules` under its **name**. When you run a file as a script, its name is
`"__main__"`, not its file name. So what happens when another module imports the script by its file name?

Two files sit in the same folder:

```text
demo/
├── counter.py
└── helper.py
```

`counter.py`:

```python
import sys

print("loading counter as", __name__)
hits = []


def hit(who):
    hits.append(who)
    return len(hits)


if __name__ == "__main__":
    import helper

    print("main sees", hit("main"))
    helper.go()
    helper.go()
    import counter

    print("same module?", counter is sys.modules["__main__"])
    print("main hits:", hits)
    print("counter hits:", counter.hits)
```

`helper.py`:

```python
import counter

print("loading helper")


def go():
    print("helper sees", counter.hit("helper"))
```

Kavya runs, from inside `demo/`:

```bash
python counter.py
```

Write exactly what the program prints, one line per printed line, in `answer.txt`.
The program never stops with an error.

## Example of the format

A program that does `print("a", 1)` and then `print([2])` prints:

```text
a 1
[2]
```
