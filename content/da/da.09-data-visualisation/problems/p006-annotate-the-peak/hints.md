## Hint 1

Which number do you need from `y`: the maximum, and the *position* of the maximum? Which Axes method draws text with an arrow, and which draws a full-width horizontal line?

## Hint 2

```text
i = index of the first maximum   (np.argmax finds the first)
ax.annotate(f"Peak: {y[i]:,.0f}", xy=(x[i], y[i]), xytext=(offset), arrowprops=dict(arrowstyle="->"))
ax.axhline(mean of y)
return ax
```
