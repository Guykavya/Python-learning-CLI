## Hint 1

What does the finalizer need to know to write `"close tmp1"`? Only the name and the log, so
pass exactly those as its arguments. Which object must you **not** pass, directly or hidden inside
a bound method? Once you have the finalizer object, which of its features give you "run at most
once" and "has it run yet?" for free?

## Hint 2

```
module level:
    instances = weakref.WeakSet()
    def release(name, log): log.append(f"close {name}")

TempResource.__init__(name, log):
    self.name = name
    log.append(f"open {name}")
    self._finalizer = weakref.finalize(self, release, name, log)
    instances.add(self)

close():             self._finalizer()          # runs once, later calls do nothing
closed (property):   return not self._finalizer.alive
__enter__:           return self
__exit__(...):       self.close(); return False

live_resources():    sorted names of r in instances if not r.closed
```
