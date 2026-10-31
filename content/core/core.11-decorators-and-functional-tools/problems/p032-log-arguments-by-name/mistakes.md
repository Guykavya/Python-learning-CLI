- Logging before binding. A bad call then leaves a misleading log line.
- Forgetting `apply_defaults()`. Then `urgent=False` is missing when the caller did not pass it.
- Joining `args` and `kwargs` by hand. You lose the parameter names and the signature order.
- Calling `inspect.signature(wrapper)` inside `wrapper` without `wraps`: the signature is
  `(*args, **kwargs)` and every line says `greet(args=(...), kwargs={...})`.
- A `shout`-like decorator without `wraps` under `log_arguments` breaks the names. That is the
  inner decorator's bug, and the reason to always use `wraps`.
- Using `str(value)` instead of `repr(value)`: `text=hi` instead of `text='hi'`.
