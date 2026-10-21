## Hint 1

Each pair is decided by its smaller value `a`, since `b = target - a`. How do you know whether
`b` is in the list fast?

## Hint 2

Make `values = set(nums)`. For each `a` in `values` with `a <= target - a`, check
`target - a in values`.

## Hint 3

When `a == target - a`, you need the value twice: `nums.count(a) >= 2` is fine here because it
can happen for at most one value. Or count with a dict.
