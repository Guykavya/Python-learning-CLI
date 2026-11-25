## Approach

`plt.subplots(2, 2)` creates 4 Axes; `c.twinx()` adds a 5th, so `len(fig.axes)` is 5.

- `a` got three `plot` calls: 3 lines, no bars, title `'lines'`.
- `b` got one `bar` call with four bars: no lines, 4 patches, title `'bars'`.
- `c` has one line; its title is `'twin'`. The two lines drawn after `twinx()` belong to `c2`, not `c`.
- `c2` has 2 lines and no title (`''`): titles are not copied to the twin.
- `d` is an empty panel: 0 lines, 0 patches, title `''`.

## Code

```text
axes in figure: 5
a 3 0 'lines'
b 0 4 'bars'
c 1 0 'twin'
c2 2 0 ''
d 0 0 ''
```

## Complexity

Not applicable (a trace problem).

## Another way

`for ax in fig.axes: print(ax.get_title(), len(ax.lines), len(ax.patches))` walks the same tree without naming each Axes.
