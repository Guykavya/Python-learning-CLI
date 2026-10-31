## Hint 1

Sort the tools by what they **look at**: ruff looks at the shape of the text and the syntax
tree, the formatter only at layout, mypy at the types flowing through the code, pytest at the
values while the code runs. For each numbered line ask: is the problem visible in the shape,
the types, or only when it runs with particular values?

## Hint 2

Structure your answer like this:

```
lines 1-5:   tool -> why (one or two sentences each); say "none" honestly for 2 and part of 5
per tool:    catches ... / misses ...
order:       which tools CHANGE files? which are slow? which need the whole project?
cost:        time per commit, false alarms, adoption work; how teams reduce each
end:         one or two sentences that answer "just run pytest"
```
