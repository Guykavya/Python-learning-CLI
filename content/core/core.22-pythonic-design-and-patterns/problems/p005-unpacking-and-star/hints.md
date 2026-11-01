## Hint 1

Every `p[0]`, `p[1]` is a name you have not given yet. If you could write the names on the
left side of `=`, what would the line look like? For `first, *rest = items`, what happens when
`items` is empty, and what must the function return then?

## Hint 2

Match the tool to the job.

```
describe_point : x, y, z = p ; f-string
split_head_tail: if not items: return None, [] ; first, *rest = items
trim_ends      : if len(items) < 2: return [] ; _, *middle, _ = items
swap_pairs     : [(b, a) for a, b in pairs]
distance       : (x1, y1), (x2, y2) = segment
fib            : a, b = b, a + b      (right side is computed first)
merge_settings : defaults | user | overrides
```
