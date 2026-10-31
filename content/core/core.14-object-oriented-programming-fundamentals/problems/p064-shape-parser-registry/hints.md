## Hint 1

A class decorator is a function that receives the class right after the `class` statement and must
**return** it. What happens to the name `Circle` if your decorator returns nothing?

`from_args` is a classmethod on `Shape`, but it reads `cls.n_args` and `cls.kind`. When you call
`Square.from_args(...)`, which values does it see?

## Hint 2

`parse_shapes` and `parse_all` share the work "number the lines, skip blank and comment lines". Put it in
a small generator that yields `(line_no, stripped_line)` and use it in both. `enumerate(lines, start=1)`
numbers every line, also the ones you skip.

In `parse_all` you create a `BadShapeLine` without raising it. How do you still give it a cause? (Either
set `bad.__cause__ = err`, or raise it `from err` inside a `try` and catch it right away.)

## Hint 3

```text
parse_shape(text):
    words = text.split(); if no words: ValueError("empty shape line")
    kind = words[0].lower()
    try: cls = SHAPES[kind]
    except KeyError as err: raise UnknownShapeError(kind) from err
    return cls.from_args(words[1:])

parse_all(lines):
    shapes, errors = [], []
    for line_no, line in numbered(lines):
        try: shapes.append(parse_shape(line))
        except (ValueError, UnknownShapeError) as err:
            bad = BadShapeLine(line_no, line, str(err)); bad.__cause__ = err; errors.append(bad)
    if errors: raise ExceptionGroup(f"{len(errors)} bad line(s)", errors)
    return shapes
```
