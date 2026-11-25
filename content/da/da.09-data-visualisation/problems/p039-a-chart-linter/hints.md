## Hint 1

Write the five checks one at a time and test each on a figure that has only that problem. Which Axes methods tell you the title, the labels, the limits and the legend? What counts as "has data"?

## Hint 2

```text
fig.canvas.draw(); issues = []
for i, ax in enumerate(fig.axes):
    skip colorbars
    title / labels / bars / legend -> append messages in that order
fonts: any(t.get_visible() and t.get_text().strip() and t.get_fontsize() < min_font for t in fig.findobj(Text))
```
