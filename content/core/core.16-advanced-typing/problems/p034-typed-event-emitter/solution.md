## Approach

`Emitter` has one type parameter, but it is a *parameter list*, not a single type: that is what a
`ParamSpec` is. Using the same `P` in `Callable[P, None]` (the handlers) and in
`*args: P.args, **kwargs: P.kwargs` (what `emit` accepts) is the whole link: a checker now knows
that `Emitter[[str, int]].emit` takes a `str` and an `int`, and that only handlers with that
signature may be registered.

Behaviour decisions, each is a classic emitter bug if missed:

- **Snapshot**: iterate over `list(self._handlers)`, so a handler that adds or removes handlers
  during an `emit` does not corrupt the loop (changing a list while iterating it skips items).
- **`once`**: store a flag with the handler rather than wrapping the function, so `off(handler)`
  still finds it. Remove the registration *before* calling, so it is gone even if it raises or if
  it emits the same event again. Removal is by identity of the stored tuple, so two registrations
  of the same function do not get mixed up.
- **`off`** compares with `==` (bound methods are new objects on every attribute access, but equal).

`EventBus` gives up on tracking parameters (`Emitter[...]`, `Callable[..., None]`, `*args: Any`),
because the argument types depend on the event name, which a `ParamSpec` cannot express.
(A `TypedDict` or a `Protocol` per event is the usual next step.)

## Code

```python
from collections.abc import Callable
from typing import Any, Generic, ParamSpec

P = ParamSpec("P")


class Emitter(Generic[P]):
    def __init__(self) -> None:
        self._handlers: list[tuple[Callable[P, None], bool]] = []

    def on(self, handler: Callable[P, None]) -> Callable[P, None]:
        self._handlers.append((handler, False))
        return handler

    def once(self, handler: Callable[P, None]) -> Callable[P, None]:
        self._handlers.append((handler, True))
        return handler

    def off(self, handler: Callable[P, None]) -> bool:
        for i, (registered, _) in enumerate(self._handlers):
            if registered == handler:
                del self._handlers[i]
                return True
        return False

    def emit(self, *args: P.args, **kwargs: P.kwargs) -> None:
        for entry in list(self._handlers):
            handler, is_once = entry
            if is_once:
                self._discard(entry)
            handler(*args, **kwargs)

    def _discard(self, entry: tuple[Callable[P, None], bool]) -> None:
        for i, current in enumerate(self._handlers):
            if current is entry:
                del self._handlers[i]
                return

    def __len__(self) -> int:
        return len(self._handlers)


class EventBus:
    def __init__(self) -> None:
        self._events: dict[str, Emitter[...]] = {}

    def on(self, name: str, handler: Callable[..., None]) -> Callable[..., None]:
        self._events.setdefault(name, Emitter()).on(handler)
        return handler

    def emit(self, name: str, *args: Any, **kwargs: Any) -> int:
        emitter = self._events.get(name)
        if emitter is None:
            return 0
        count = len(emitter)
        emitter.emit(*args, **kwargs)
        return count

    def names(self) -> list[str]:
        return sorted(n for n, e in self._events.items() if len(e) > 0)
```

## Complexity

`on`, `once`: O(1). `off`: O(h) for h handlers. `emit`: O(h) plus the handlers' own work.
`EventBus.emit`: O(1) lookup plus the emitter's `emit`.

## Another way

With Python 3.12 syntax: `class Emitter[**P]:` needs no `ParamSpec(...)` line. A dictionary
from handler to count would make `off` O(1) but loses the order of calls. Libraries often return a
"disconnect" function from `on` instead of having an `off` method, which solves the "same function
registered twice" question in a cleaner way.
