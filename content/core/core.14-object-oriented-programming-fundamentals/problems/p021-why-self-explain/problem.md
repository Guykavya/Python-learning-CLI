# Explain: what `self` is and why Python makes it explicit

Ravi is learning classes. He wrote this and is confused:

```python
class Counter:
    def __init__(self):
        count = 0

    def tick():
        self.count += 1


c = Counter()
c.tick()
```

The last line fails with:

```text
TypeError: Counter.tick() takes 0 positional arguments but 1 was given
```

"But I gave it **zero** arguments!", he says. "And why do I have to write `self` everywhere? Java
doesn't need it."

In `answer.md` (about 150 to 300 words), explain:

1. What `self` is. Which object is it when you call `c.tick()`?
2. What `c.tick()` turns into, written with the class name. Use this to explain the "1 was given"
   in the error message.
3. The **second** bug in Ravi's class: what does `count = 0` in `__init__` do, and what should it be?
   What error would he get next, after fixing `tick`?
4. Why Python makes `self` explicit instead of hiding it. Give at least two reasons (for example:
   reading code, local variables vs attributes, calling a parent's method, functions and methods being
   the same thing).
5. Is the name `self` required by the language?

## Example of the level of detail

"`self` is an ordinary parameter. When you write `c.tick()`, Python finds `tick` in the class `Counter`
and passes `c` as the first argument." A good answer goes on like this for each point.
