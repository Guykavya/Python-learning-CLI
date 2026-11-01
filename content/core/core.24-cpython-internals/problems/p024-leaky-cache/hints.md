## Hint 1

For each report, find **who still holds a reference** to the object that should be gone:

1. What does a bound method object keep inside it? (`w.on_save.__self__`) Who keeps the bound
   method? Why can you not simply store `weakref.ref(w.on_save)`? (Try it: the bound method is a
   temporary object.) And why would a weak reference to a lambda be a disaster?
2. Draw the arrows between a `Document`, its `pages` list and a `Page`. Is there a loop? What can
   reference counting not free, and who frees it instead (and when)?
3. Which object holds every described object as a key? Is there a dictionary that does not keep its
   keys alive?

## Hint 2

```
EventBus:
    subscribe(cb):  store WeakMethod(cb) if inspect.ismethod(cb), else a small object that
                    returns cb when called (so both kinds are "call it to get the callback")
    live():         callbacks = [ref() for ref in subscribers if ref() is not None]
                    and keep only the live refs
    publish:        for cb in live(): cb(event)
    subscriber_count: len(live())
    unsubscribe(cb): find the ref with ref() == cb and remove it; none found -> ValueError

Page:
    __init__: self._document = weakref.ref(document)
    document (property): return self._document()

_cache = weakref.WeakKeyDictionary()      # describe() itself does not change
```
