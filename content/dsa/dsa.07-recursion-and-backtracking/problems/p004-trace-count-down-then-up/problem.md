# Trace: count down, then up

Predict **exactly** what this program prints. Do not run it.

```python
def show(n):
    if n == 0:
        print("base")
        return
    print("down", n)
    show(n - 1)
    print("up", n)


show(3)
print("done")
```

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it (for example `down 3`).

## How to work

Each call of `show` does three things in order: print `down`, call itself, print `up`. The `up` line of a call can only run **after** the inner call has completely finished.
Draw the stack: `show(3)` waits for `show(2)`, which waits for `show(1)`, which waits for `show(0)`.

## After you answer

1. Which line is printed by the deepest call?
2. Move the `print("up", n)` line before the recursive call. What changes?
3. How many lines does `show(10)` print?
