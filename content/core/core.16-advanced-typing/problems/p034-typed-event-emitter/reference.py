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
