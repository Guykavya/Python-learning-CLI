## Hint 1

The hook is just a function you define inside `install_recorder`, so it can see the `records`
list through the enclosing scope. What should its parameters be so that `breakpoint()`,
`breakpoint(1)` and `breakpoint(x=2)` all work?

## Hint 2

`sys._getframe(0)` is the hook's own frame; `sys._getframe(1)` is one level out: the function
that wrote `breakpoint()`. Why must you wrap `f_locals` in `dict(...)` instead of storing it
directly? (Think: what happens if the variable changes after the record is taken, and what
`f_locals` really is.)

## Hint 3

```
install_recorder():
    records = []
    def hook(*args, **kwargs):
        frame = sys._getframe(1)
        records.append({"function": frame.f_code.co_name,
                        "locals": dict(frame.f_locals)})
    sys.breakpointhook = hook
    return records

uninstall():
    sys.breakpointhook = sys.__breakpointhook__
```
