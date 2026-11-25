# Anatomy by hand

Chapter section 3. Every chart is a tree: a Figure holds Axes, an Axes holds lines and bars (patches). Counting them by hand is the
best test of whether you see that tree.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2)
a, b, c, d = axes.flat
for k in range(3):
    a.plot([0, 1, 2], [k, k + 1, k + 2])
a.set_title("lines")
b.bar(["w", "x", "y", "z"], [4, 3, 2, 1])
b.set_title("bars")
c.plot([0, 1], [0, 1])
c2 = c.twinx()
c2.plot([0, 1], [5, 3])
c2.plot([0, 1], [4, 4])
c.set_title("twin")
print("axes in figure:", len(fig.axes))
for name, ax in [("a", a), ("b", b), ("c", c), ("c2", c2), ("d", d)]:
    print(name, len(ax.lines), len(ax.patches), repr(ax.get_title()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. `twinx()` creates a **new Axes** on top of
the old one, sharing the x axis.

Do not run the code before you have written your answer.

## Example

If a panel had one line and no bars and the title "t", its line would read `e 1 0 't'`.

## After you answer

- Why does `d` still count as an Axes although nothing was drawn on it?
- Which Axes does the title "twin" belong to, `c` or `c2`?
