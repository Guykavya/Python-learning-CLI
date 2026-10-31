## Hint 1

For each row of the table ask two questions: what is the *type* of the thing, and what are its *limits*? Every strategy takes arguments for the limits
(`min_value`, `max_value`, `min_size`, `max_size`, `alphabet`). What do you pass for "lowercase letters only"? (`import string` has a ready-made constant.)

## Hint 2

Strategies nest like the data does: a dictionary strategy takes a strategy for the keys and one for the values; a list strategy takes one for the
elements. `st.floats` accepts `min_value` and `max_value`, and when both are given it never produces `nan` or infinity. For a class, `st.builds(Point, x=..., y=...)` calls
`Point(x=..., y=...)` with generated values. For "this or that", `st.one_of`.

```
small_ints  = integers(min_value=1, max_value=100)
usernames   = text(alphabet=string.ascii_lowercase, min_size=3, max_size=12)
digit_lists = lists(integers(0, 9), min_size=1, max_size=5)
stock       = dictionaries(text(<letters>, 1..5), floats(0, 100), min_size=1, max_size=4)
points      = builds(Point, x=integers(-10, 10), y=integers(-10, 10))
id_or_none  = one_of(none(), integers(1, 999))
weekdays    = sampled_from(["mon", ..., "sun"])
```
