# An event bus of closures

Write `make_event_bus()` that returns a dict of three functions sharing private state:

- `on(event, handler)`: register `handler` (a function) for the event name `event`. The same
  handler may be registered more than once; it is then called once per registration.
- `off(event, handler)`: remove the **first** registration of `handler` for `event`; return
  `True` if one was removed, `False` otherwise.
- `emit(event, *args, **kwargs)`: call every handler registered for `event`, in registration
  order, with exactly those arguments, and return a list of their return values. An event with no
  handlers returns `[]`.

Separate buses are independent. Registering or removing handlers **during** an `emit` must not
affect which handlers that `emit` calls (loop over a copy).

**Example**

```python
bus = make_event_bus()
on, off, emit = bus["on"], bus["off"], bus["emit"]

def greet(name):
    return "hello " + name

def shout(name, punct="!"):
    return name.upper() + punct

on("join", greet)
on("join", shout)
emit("join", "asha")                 # ['hello asha', 'ASHA!']
off("join", greet)                   # True
emit("join", "ravi", punct="?")      # ['RAVI?']
off("join", greet)                   # False
emit("leave")                        # []
```

`emit` passes the **same** arguments to every handler of an event, so they must all accept them:
`emit("join", "ravi", punct="?")` only works once `greet`, which has no `punct` parameter, is gone.
