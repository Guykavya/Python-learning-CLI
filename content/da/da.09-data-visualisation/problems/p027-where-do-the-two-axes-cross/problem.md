# Where do the two axes cross?

Chapter section 6.2. With two y axes, the picture of "which line is higher" depends on the **limits** of each axis, not only on the data.
This program counts the months in which the line `a` is **drawn above** the line `b`, measuring each line as a **fraction of its own axis** (0 = bottom, 1 = top).

```python
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

a = np.array([40, 42, 44, 46.0])
b = np.array([30, 34, 38, 42.0])


def months_a_above_b(ylim_left, ylim_right):
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    ax.plot(a)
    ax2.plot(b)
    ax.set_ylim(*ylim_left)
    ax2.set_ylim(*ylim_right)
    l = (ax.lines[0].get_ydata() - ax.get_ylim()[0]) / np.diff(ax.get_ylim())[0]
    r = (ax2.lines[0].get_ydata() - ax2.get_ylim()[0]) / np.diff(ax2.get_ylim())[0]
    plt.close(fig)
    return int((l > r).sum())


for left, right in [((0, 50), (0, 50)), ((0, 50), (0, 40)), ((0, 50), (20, 40)), ((0, 100), (0, 40))]:
    print(left, right, months_a_above_b(left, right), "of 4")
```

In the data, `a` is higher than `b` in **every** month. Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.
Do not run the code before you have written your answer.

## Example

For `ylim_left = (0, 100)` and `ylim_right = (0, 100)`, `l = 0.40, 0.42, 0.44, 0.46` and `r = 0.30, 0.34, 0.38, 0.42`: all four months, so the line would be `(0, 100) (0, 100) 4 of 4`.

## After you answer

- In which of your four lines does the picture contradict the data?
- What would you plot instead, if both series have the same unit?
