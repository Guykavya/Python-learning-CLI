- Using `"  " * depth` again for the `->` line after `depth` was lowered or changed by inner
  calls. Save the indent in a local variable first.
- Lowering the depth only after a normal return. After an exception every later call is
  indented too far. Use `finally`.
- Swallowing the exception: logging `!!` but not using `raise`.
- Putting `depth = 0` in `trace_calls`. Then two functions decorated with the same log and
  factory would share one depth (and `outer` calling `inner` would indent `inner`).
- Using `str` instead of `repr`: `greet(ann)` instead of `greet('ann')`.
