# log_arguments: name every argument with inspect.signature

A log line like `send(1, 'hi')` does not tell you which value is which. A better log names every
parameter and shows the defaults too: `send(user=1, text='hi', urgent=False)`.

The `inspect` module can do this. `inspect.signature(func)` describes the parameters of a
function, and its `bind` method matches a call's arguments to the parameter names:

```python
import inspect

def send(user, text, urgent=False):
    ...

sig = inspect.signature(send)
bound = sig.bind(1, "hi")          # raises TypeError if the call does not fit
bound.apply_defaults()             # fill in parameters that were not passed
bound.arguments                    # {'user': 1, 'text': 'hi', 'urgent': False}
```

Write a decorator factory `log_arguments(log)` in `solution.py`:

1. On each call, bind the arguments, apply the defaults, and append one line to `log`:
   `name(param=repr(value), param=repr(value), ...)` in parameter order.
2. Then call the function and return its result.
3. If the arguments do not fit the signature, `bind` raises `TypeError`. Let it go up: nothing is
   logged and the function is **not** called.
4. Use `functools.wraps`. Then `inspect.signature(decorated)` still shows the real parameters,
   because `inspect.signature` follows the `__wrapped__` attribute that `wraps` sets.
5. This also means `log_arguments` works on top of **another** decorator, as long as that one
   used `wraps` too. Look at the real parameters with `inspect.signature(func)`; do not try to
   unwrap the function yourself.

**Example**

```python
log = []

@log_arguments(log)
def send(user, text, urgent=False):
    return f"sent to {user}"

send(1, "hi")                    # "sent to 1"
send(2, text="yo", urgent=True)
log
# ["send(user=1, text='hi', urgent=False)",
#  "send(user=2, text='yo', urgent=True)"]
```

A `*args` parameter shows as a tuple, for example `total(first=1, rest=(2, 3))`.
