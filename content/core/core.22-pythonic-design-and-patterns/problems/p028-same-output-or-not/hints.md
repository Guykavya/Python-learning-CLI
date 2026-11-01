## Hint 1

Take the pairs one at a time and ask the same question: *is there any state that outlives a
single use?* In pair 1: what is `i` when the lambdas are finally called? In pair 2: how many
list objects exist for `bag`? In pair 3: what is left in the generator after `sum`? In pair 4:
does a comprehension variable stay visible after it? In pair 5: does `v == None` ever differ
from `v is None` for these values?

## Hint 2

```
1: lambdas close over the VARIABLE i (final value 2), not its value at each step.
   after: i=i copies the value into a default at creation time.
2: before_2("a") and before_2("b") return THE SAME list; print shows it after both appends.
3: sum(squares) uses up the generator; max on an exhausted generator gives the default -1.
4: the comprehension has its own scope; the for loop rebinds the outer i.
5: 0, "" and [] are falsy but are not equal to None.
```

Remember the last two lines: `before_2` still holds `['a', 'b']` from pair 2 when it is called with `"c"`.
