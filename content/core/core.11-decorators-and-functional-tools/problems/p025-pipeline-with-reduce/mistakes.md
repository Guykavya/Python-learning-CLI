- `reduce(lambda f, g: g(f), funcs)` without a start value. The first "accumulator" is then a
  function, not the input, and an empty pipeline raises `TypeError`.
- Applying the steps right to left. `pipeline` reads like a recipe: first step first.
- Checking `callable` inside `run`. The error then shows up far from the line that built the
  bad pipeline.
- Calling the steps while building, for example `funcs = [f() for f in funcs]`.
- Storing `funcs` as a generator. It is used up after the first run, and the second run returns
  the input unchanged.
