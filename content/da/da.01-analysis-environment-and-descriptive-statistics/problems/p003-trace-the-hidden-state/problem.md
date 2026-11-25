# Trace the hidden state

Chapter section 3.1. The `MiniKernel` below is the chapter's toy kernel: cells share one namespace, `run` prints a header line `[n] >>> source` and then executes the source, and `restart` forgets everything. The page lists five cells, but the reader runs them **out of order**, one of them twice, and one of them redefines a variable.

```python
class MiniKernel:
    def __init__(self):
        self.namespace = {}
        self.run_count = 0

    def run(self, source):
        self.run_count += 1
        print(f"[{self.run_count}] >>> {source}")
        exec(source, self.namespace)

    def restart(self):
        self.namespace = {}
        self.run_count = 0
        print("--- kernel restarted: all variables forgotten ---")


page = [
    "price = 50",                                  # cell 0
    "total = price * 3",                           # cell 1
    "print('total is', total)",                    # cell 2
    "price = 80",                                  # cell 3
    "print('price', price, 'total', total)",       # cell 4
]

kernel = MiniKernel()
for index in [0, 1, 2, 3, 4, 2, 1, 2]:
    kernel.run(page[index])

kernel.restart()
try:
    kernel.run(page[2])
except NameError as error:
    print("NameError:", error)
kernel.run(page[0])
kernel.run(page[1])
kernel.run(page[2])
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Remember: `print` inside a cell prints its own line right after the header line; the counter `[n]` restarts at 1 after `restart()`; and the traceback is caught, only the `NameError:` line is printed.

Do not run the code before you have written your answer.

## Answer format

One printed line per line of `answer.txt`, exactly as Python prints it (including the `--- kernel restarted ... ---` line).

## After you answer

- After the first `price = 80` (cell 3), which of the printed totals was out of date, and why did the page look correct?
- What does the restart show about the notebook that was "working" a moment ago?
