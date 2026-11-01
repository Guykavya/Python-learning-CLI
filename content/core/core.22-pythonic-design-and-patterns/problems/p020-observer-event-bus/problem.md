# Observer: an event bus

The **observer pattern** lets code announce "something happened" without knowing who cares.
Listeners subscribe; the announcer publishes. `starter.py` has a first draft of an `EventBus`
that works only when nothing goes wrong.

Copy it to `solution.py` and make `EventBus` follow these rules.

- `subscribe(event, fn)` adds `fn` to the handlers of `event` and **returns an unsubscribe
  function** (call it with no arguments to remove exactly this subscription).
  Calling it a second time does nothing. Subscribing the *same function* twice makes two
  separate subscriptions; each unsubscribe function removes only its own.
- `publish(event, **data)` calls every handler of `event` as `fn(**data)`, **in the order
  they subscribed**.
- A handler that raises must **not** stop the others. `publish` collects the exceptions
  (in handler order) and returns them as a list. If nothing failed, or nobody listens, it returns `[]`.
- A handler may subscribe or unsubscribe (even itself) while `publish` is running. This must be
  safe, and the change takes effect from the **next** `publish`: the current publish runs the
  handlers that were subscribed when it started.

**Example**

```python
bus = EventBus()
log = []
off = bus.subscribe("saved", lambda **d: log.append(d["id"]))
bus.subscribe("saved", lambda **d: 1 / 0)
bus.publish("saved", id=7)      # [ZeroDivisionError('division by zero')]; log is [7]
off()
bus.publish("saved", id=8)      # log is still [7]
```
