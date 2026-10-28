## Approach

Python evaluates the decorator expressions top to bottom: `tag("b")` prints `make b`, then `tag("i")`
prints `make i`. Then it applies them bottom up, nearest to the function first: `decorate` for `i` runs
(`decorate i`), then `decorate` for `b` wraps that result (`decorate b`). So
`show = b_decorate(i_decorate(show))`.

When `show("hi")` runs, the outermost wrapper is `b`: `enter b`. It calls the `i` wrapper: `enter i`.
That calls the real body: `body`. Going back out, `i` finishes first (`exit i`) and returns `<i>hi</i>`.
Then `b` finishes (`exit b`) and returns `<b><i>hi</i></b>`.

## Output

```text
make b
make i
decorate i
decorate b
ready
enter b
enter i
body
exit i
exit b
<b><i>hi</i></b>
```

## Complexity

O(1).

## Another way

Remember it as reading order: the decorator on top is the outermost layer. It runs first on the way in
and last on the way out, like the first `<b>` tag that opens first and closes last.
