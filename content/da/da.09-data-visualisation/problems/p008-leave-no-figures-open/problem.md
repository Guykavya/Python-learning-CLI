# Leave no figures open

Chapter section 3. `plt.subplots()` registers the new figure in a global list, and the figure stays alive until you close it. A loop that
draws 200 charts without closing them keeps 200 figures in memory (and matplotlib warns after 20).

Write `render_all(frames, folder)`:

- `frames` is a dict `{name: DataFrame}`; each DataFrame has columns `label` and `value`;
- for each frame draw a vertical bar chart (`label` on x, `value` as height) and save it to `folder/<name>.png`;
- return the list of saved `Path`s, in the order of `frames`;
- when the function returns **or raises**, no figure of yours may stay open: `plt.get_fignums()` must be `[]`.

If a frame is broken (a column is missing) the error should reach the caller, and the figures must still be closed.

## Example

```python
paths = render_all({"q1": df1, "q2": df2}, folder)   # [folder/q1.png, folder/q2.png]
plt.get_fignums()                                    # []
```
