# An event bus with duck-typed listeners

An **event bus** lets parts of a program talk without knowing each other: one part *publishes*
`"order_paid"`, and every object that *subscribed* to that event gets it. One broken listener must not
stop the others, so failures are collected and reported together at the end.

In `solution.py` write:

### `class Event`

`Event(name, payload=None)` with the attributes `name` and `payload`. Nothing else.

### `class EventBus`

- `subscribe(event_name, listener)`: a **listener** is any object with a callable `handle` attribute
  (duck typing; no base class needed). If `listener` has no `handle`, or it is not callable
  (`callable(x)`), raise `TypeError("listener needs a handle(event) method")`. Subscribing the **same
  object** (`is`) to the same event a second time does nothing. Listeners are called in the order they
  subscribed. The event name `"*"` means "every event".
- `unsubscribe(event_name, listener)`: remove that object from that event. If it is not subscribed
  there, raise `ValueError(f"listener is not subscribed to {event_name!r}")`.
- `listeners(event_name)`: a **new** list with the listeners of that exact name (no `"*"` ones), in
  order. Unknown names give `[]`.
- `publish(event_name, payload=None)`:
  1. builds **one** `Event(event_name, payload)`;
  2. calls `listener.handle(event)` for every listener of `event_name`, then for every `"*"` listener
     (a listener subscribed to both gets the event twice);
  3. if a listener raises an `Exception`, `publish` remembers it and **continues** with the next one.
     Before remembering, it adds a note with `exc.add_note(f"listener: {type(listener).__name__}")`;
  4. after all listeners ran: if any failed, raise
     `ExceptionGroup(f"{n} listener(s) failed for {event_name!r}", errors)` with the errors in the
     order they happened; otherwise return the number of `handle` calls made.
  5. Publishing `"*"` itself is not allowed: `ValueError("cannot publish '*'")`.
  6. Listeners may subscribe or unsubscribe **while** an event is being published. Such changes count
     from the **next** `publish`; the current one uses the listeners as they were when it started.

## Example

```python
class Printer:
    def handle(self, event):
        print("got", event.name, event.payload)

class Broken:
    def handle(self, event):
        raise RuntimeError("boom")

bus = EventBus()
p = Printer()
bus.subscribe("order_paid", p)
bus.subscribe("order_paid", Broken())
bus.subscribe("*", p)
bus.publish("order_paid", 499)
# got order_paid 499
# got order_paid 499          (again, as the "*" listener)
# then: ExceptionGroup: 1 listener(s) failed for 'order_paid'
#       its one exception is RuntimeError('boom') with the note 'listener: Broken'

bus.publish("user_joined")     # got user_joined None   -> returns 1
bus.subscribe("x", object())   # TypeError: listener needs a handle(event) method
```
