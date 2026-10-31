## Hint 1

Rewrite the stack without `@`. The two `tag(...)` expressions are evaluated top to bottom first.
Then the decorator **nearest** to `def` is applied first:
`show = tag("b")(tag("i")(show))`. In what order do `make` and `decorate` print?

## Hint 2

The outer wrapper (`b`) runs first when you call `show`, but it reaches the body only through the
inner wrapper (`i`). Think of nested boxes: you enter `b`, then `i`, then the body; you leave `i`
first, then `b`. Each exit wraps the text it got from inside.
