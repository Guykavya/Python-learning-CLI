## Hint 1

Start with the plain version, no types: a list of handlers and four methods. Which parts of the
behaviour are tricky? (`once`, and what happens when a handler changes the list during `emit`.) Then ask what a handler's parameter list has to do with `emit`'s parameter list.

## Hint 2

Store registrations as `(handler, is_once)` pairs so that `off` can remove a `once` handler too (no wrapper function). In `emit`, loop over `list(self._handlers)` (a snapshot). For a once entry, remove **that registration** from the live list *before* calling the handler. For the types: `P = ParamSpec("P")`, `class Emitter(Generic[P])`, handler `Callable[P, None]`, and `emit(self, *args: P.args, **kwargs: P.kwargs)`. The bus keeps a `dict[str, Emitter[...]]`.

## Hint 3

```
class Emitter(Generic[P]):
    __init__:  self._handlers: list[tuple[Callable[P, None], bool]] = []
    on:   append (handler, False); return handler
    once: append (handler, True);  return handler
    off:  first i where registered == handler -> del, True ; else False
    emit: for entry in list(self._handlers):
              handler, is_once = entry
              if is_once: remove entry (compare with `is`) from self._handlers
              handler(*args, **kwargs)

class EventBus:
    _events: dict[str, Emitter[...]]
    on:   setdefault(name, Emitter()).on(handler); return handler
    emit: emitter = get(name); None -> 0 ; count = len(emitter); emitter.emit(...); return count
    names: sorted(n for n, e in items if len(e) > 0)
```
