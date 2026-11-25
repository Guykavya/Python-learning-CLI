## Hint 1

Which pandas argument checks the *relationship* between the two tables, and what happens when it does not hold (do you
need to catch anything)? After the merge, which two numbers must you compare, and for which kind of join is the
comparison meaningful? What is the text when the caller gives no label?

## Hint 2

```text
out = left.merge(right, on=on, how=how, validate=validate)      # MergeError comes from pandas by itself
if how == "left" and len(out) != len(left):
    name = label or f"join on {on}"
    raise AssertionError(f"{name}: rows changed {len(left)} -> {len(out)} (fan-out or a lost key?)")
return out
```
