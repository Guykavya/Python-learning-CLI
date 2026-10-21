## Hint 1

`zip` silently stops at the shorter input. Why must you compare the lengths **before** looping?

## Hint 2

Check `len(names) != len(scores)` first. Then `for name, score in zip(names, scores):`.

## Hint 3

Add each `int(score)` to a total inside the loop. The average is `total / len(names)`.
