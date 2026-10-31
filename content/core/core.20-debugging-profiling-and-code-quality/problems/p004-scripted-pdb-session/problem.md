# Trace: a scripted pdb session

`pdb.Pdb` is an ordinary class. Give it a file-like `stdin` and it reads its commands from
there instead of the keyboard, so a whole debugging session can be written down and replayed.
Its own messages (prompts, `-> line` listings) go to `stdout`, which here is a `StringIO` that
nobody prints, so the only output is what the program prints at the end.

Each `!...` command runs a Python statement **inside the frame where pdb is stopped**, with
that frame's variables. Here it appends a snapshot to the global list `seen`.

Rules you need:

- `runcall(f, *args)` calls `f` and stops at its **first line** (line 8).
- `b 11, qty > 1` sets breakpoint 1 on line 11 with a condition: pdb stops there only when the
  condition is true. A line is reported **before** it runs.
- `c` continues until a breakpoint stops it; `n` runs the current line and stops at the next
  line of this function (in a `for` loop, after the body comes the `for` line again).
- `cl 1` deletes breakpoint 1; `b 12` adds breakpoint 2.

What does this program print?

```python
import io
import pdb

seen = []


def total_price(items):
    total = 0                       # line 8
    for name, price, qty in items:  # line 9
        cost = price * qty          # line 10
        total += cost               # line 11
    return total                    # line 12


cart = [("pen", 10, 3), ("book", 120, 1), ("bag", 450, 2), ("ink", 5, 1)]

commands = [
    "b 11, qty > 1",
    "c",
    "!seen.append(('A', name, cost, total))",
    "n",
    "!seen.append(('B', name, cost, total))",
    "n",
    "!seen.append(('C', name, cost, total))",
    "c",
    "!seen.append(('D', name, cost, total))",
    "cl 1",
    "b 12",
    "c",
    "!seen.append(('E', name, cost, total))",
    "c",
]

screen = io.StringIO()
debugger = pdb.Pdb(stdin=io.StringIO("\n".join(commands) + "\n"),
                   stdout=screen, nosigint=True, readrc=False)
result = debugger.runcall(total_price, cart)

for entry in seen:
    print(*entry)
print("result", result)
```

**Example**: the first line is `A pen 30 0`. The breakpoint condition is true for the pen
(`qty` is 3), and at line 11 `cost` is already 30 but `total += cost` has not run yet.

Write in `answer.txt` the lines the program prints, in order.

Save it as `demo.py` and run `python demo.py` to check yourself. To see pdb's own side of the
conversation, add `print(screen.getvalue())` before the last loop (its exact wording differs
between Python versions, which is why it is hidden here).
