## Hint 1

Why can a list comprehension with `with open(...)` inside not work? (Each file would be closed as soon as its own `with` ends.) What object can hold *several* open resources and close them all together later?

## Hint 2

`stack.enter_context(cm)` enters the context manager `cm` (calling `__enter__`) and returns what `__enter__` returned, here the file; the stack remembers to call `__exit__` at the end. Write `files = [stack.enter_context(open(p)) for p in paths]` inside `with ExitStack() as stack:` and do all the reading inside that block.

## Hint 3

```
read_all: with ExitStack() as stack:
              files = [stack.enter_context(open(p)) for p in paths]
              return [f.read() for f in files]
merge_lines: same; return [tuple(line.rstrip("\n") for line in lines) for lines in zip(*files)]
```
Both `return`s sit inside the `with`: the files close when the function leaves the block.
