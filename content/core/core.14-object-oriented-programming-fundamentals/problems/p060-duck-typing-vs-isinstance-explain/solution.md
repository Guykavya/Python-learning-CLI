## Approach

Ask what an object must be able to **do**, and check that (chapter section 15). Concrete-type checks
(`isinstance(x, list)`) reject objects that would work. Duck typing accepts them. Between the two
duck-typing styles, EAFP is usually preferred in Python, as long as the `try` block is small. When you
do need a type check, check against an abstract base class from `collections.abc`, which describes a
behaviour (chapter section 16).

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Run the experiment: put the three versions and `Shout` into a file, call each with `open("out.txt", "w")`,
`io.StringIO()` and `Shout()`, and print what happens. Then add the typo `self.part` to `Shout.write` and
see which version gives an honest error. Try `isinstance(range(5), collections.abc.Iterable)` and
`isinstance(range(5), list)` too.
