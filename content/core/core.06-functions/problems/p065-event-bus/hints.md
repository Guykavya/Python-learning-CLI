## Hint 1

What private data does the bus need? Which shape answers 'all handlers for this event, in order' fastest?

## Hint 2

A dict from event name to a list of handlers. `setdefault(event, []).append(handler)` registers.

## Hint 3

```
def make_event_bus():
    handlers = {}
    def on(event, handler): handlers.setdefault(event, []).append(handler)
    def off(event, handler):
        lst = handlers.get(event, [])
        if handler in lst: lst.remove(handler); return True
        return False
    def emit(event, *args, **kwargs):
        return [h(*args, **kwargs) for h in list(handlers.get(event, []))]
    return {"on": on, "off": off, "emit": emit}
```
