# A typed event emitter

An event emitter keeps a list of handler functions and calls them all when something happens.
Without types, nothing says what arguments an event carries. With a `ParamSpec` the **emitter
itself is generic over the handlers' parameter list**: an `Emitter[[str, int]]` accepts only
handlers that take `(str, int)`, and its `emit` only accepts a `str` and an `int`.

Write in `solution.py`:

### `Emitter`

```python
P = ParamSpec("P")

class Emitter(Generic[P]):
    def __init__(self) -> None: ...
    def on(self, handler: Callable[P, None]) -> Callable[P, None]: ...
    def once(self, handler: Callable[P, None]) -> Callable[P, None]: ...
    def off(self, handler: Callable[P, None]) -> bool: ...
    def emit(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def __len__(self) -> int: ...
```

(`class Emitter[**P]:` is the Python 3.12+ spelling; both are accepted.)

- `on(handler)` registers the handler and **returns it**, so it also works as a decorator
  (`@emitter.on`). The same function may be registered twice (it is then called twice).
- `once(handler)` registers a handler that is removed **before** its first call, so it runs for
  one `emit` only. Returns the handler.
- `off(handler)` removes the **first** registration of that handler (a `once` registration too)
  and returns `True`; returns `False` if it was not registered.
- `emit(*args, **kwargs)` calls every registered handler in registration order with the same
  arguments. It works on a **snapshot** of the handlers: a handler that registers or removes
  handlers during an `emit` does not change who is called in this emit. An exception from a
  handler propagates (the later handlers are not called).
- `len(emitter)` is the number of registrations.

### `EventBus`

A bus has several named emitters whose parameters are not tracked by the type system:

```python
class EventBus:
    def __init__(self) -> None: ...
    def on(self, name: str, handler: Callable[..., None]) -> Callable[..., None]: ...
    def emit(self, name: str, *args: Any, **kwargs: Any) -> int: ...
    def names(self) -> list[str]: ...
```

- `on` registers on the emitter for that event name (create it when first used); returns the handler.
- `emit` calls all handlers of that event with the arguments and returns how many handlers were
  registered at the moment of the call (`0` for an unknown name: no error).
- `names()` is the sorted list of event names that have at least one handler.

Use an `Emitter` inside the bus (it is `Emitter[...]`: any parameters).

The tests check the generic structure (`__parameters__`, the `ParamSpec` in each hint, `P.args`
and `P.kwargs` on `emit`), and also the behaviour. They do not need mypy.

**Example**

```python
greet: Emitter[[str]] = Emitter()

@greet.on
def hello(name: str) -> None:
    print("hello", name)

greet.emit("Ada")          # prints: hello Ada
greet.emit(3)              # a type checker reports this; at run time it also calls hello(3)
```

**Remember**: the `[[str]]` in `Emitter[[str]]` is a **list of parameter types**, the same shape as
the first part of `Callable[[str], None]`.
