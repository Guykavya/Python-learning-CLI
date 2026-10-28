## Hint 1

For `apply_twice`, what do you get from `f(x)`? What happens if you give that value to `f` again?

## Hint 2

For `compose`, the job is to *build* a function, not to call one. Can you define a function inside `compose`
that uses `f` and `g`, and then return it without brackets?

## Hint 3

```
def compose(f, g):
    def composed(x):
        return f(g(x))
    return composed      # no () here
```
