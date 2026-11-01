# Trace: what a child process changes

A child process gets its **own memory**. With the **spawn** start method (the default on
Windows and macOS, and the safest choice everywhere) the child is a brand-new Python
interpreter that:

1. **imports your script** again, under the name `__mp_main__` instead of `__main__`, so all
   top-level code outside the `if __name__ == "__main__":` block runs again in the child;
2. then calls the target function with the arguments you gave.

Nothing the parent did inside the `__main__` block is copied into the child.

This program is saved as `shared_list.py` and run with `python shared_list.py`. Every `print`
uses `flush=True` so that lines from the two processes appear in the order they happen, and
each `join()` makes the parent wait until the child has finished. What does it print?

```python
import multiprocessing as mp

items = ["start"]
print("loading module as", __name__, flush=True)


def child(tag):
    items.append(tag)
    print("child sees", items, flush=True)


if __name__ == "__main__":
    mp.set_start_method("spawn")
    items.append("parent")
    print("parent before", items, flush=True)

    p = mp.Process(target=child, args=("one",))
    p.start()
    p.join()
    print("exit code", p.exitcode, flush=True)
    print("parent after", items, flush=True)

    child("main")
    print("parent now", items, flush=True)

    q = mp.Process(target=child, args=("two",))
    q.start()
    q.join()
    print("parent end", items, flush=True)
```

**Example**: the first line is `loading module as __main__`. The parent runs the script
directly, so its module name is `__main__`.

Write in `answer.txt` the lines the program prints, in order.
