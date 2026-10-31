# Read a traceback

The first question when a program crashes is **"where exactly did it fail?"** A traceback
answers it, but you have to know where to look: frames are listed **outermost first**, so the
line that actually raised is the **last** `File ...` line. When one exception happens while
another is being handled, Python prints **several** tracebacks joined by a sentence such as
`During handling of the above exception, another exception occurred:`. The one that reached
you, the one you must fix first, is the **last** one printed.

Write `blame(tb_text: str) -> tuple[str, int, str]` in `solution.py`. It takes the full text of
a traceback (exactly as Python printed it) and returns `(file, line, function)` for the
**innermost frame of the last traceback**.

Rules:

- A frame line starts with **exactly two spaces**, then `File "<file>", line <number>`, and
  usually `, in <function>`. Source lines under it (indented more) and the final
  error message must be ignored, even if they contain `File "...", line ...`.
- A `SyntaxError` traceback ends with a frame line that has **no** `, in <function>` part.
  Return `""` as the function in that case.
- `line` is an `int`.
- If the text has no frame line at all, raise `ValueError`.

**Example**

```python
tb = '''Traceback (most recent call last):
  File "/home/you/shop.py", line 14, in <module>
    main()
  File "/home/you/shop.py", line 10, in main
    print(price("pen"))
          ~~~~~^^^^^^^
  File "/home/you/shop.py", line 6, in price
    return PRICES[name] * 1.18
           ~~~~~~^^^^^^
KeyError: 'pen'
'''
blame(tb)    # ('/home/you/shop.py', 6, 'price')
```

And for a chained traceback:

```text
Traceback (most recent call last):
  File "/home/you/cfg.py", line 3, in load
    return int(text)
ValueError: invalid literal for int() with base 10: 'abc'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/you/cfg.py", line 9, in <module>
    load("abc")
  File "/home/you/cfg.py", line 5, in load
    raise RuntimeError("bad config")
RuntimeError: bad config
```

the answer is `('/home/you/cfg.py', 5, 'load')`: the last traceback, its last frame.
