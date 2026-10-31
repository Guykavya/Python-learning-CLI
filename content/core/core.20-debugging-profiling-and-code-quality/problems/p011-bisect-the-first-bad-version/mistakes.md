- Using `hi = len(versions) - 1` and returning `versions[lo]` without checking it. Then "nothing
  is bad" returns the last version, a wrong blame.
- `hi = mid - 1` when `mid` is bad. `mid` itself may be the first bad one, so it must stay in
  the range.
- Testing `versions[lo]` again at the end "to be sure". With `hi = n - 1` that extra call is
  needed (it is how you notice "none bad"), and it fits the limit; with `hi = n` it is wasted.
- `while lo <= hi` with `hi = mid`: when `lo == hi` the loop never ends.
- Searching for a version that "looks bad" and returning the first one found. Bisection finds
  the **boundary**, not just any bad version.
- Sorting `versions`. The list order is history order; sorting would break the "good then bad"
  shape.
