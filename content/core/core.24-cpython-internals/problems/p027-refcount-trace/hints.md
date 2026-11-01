## Hint 1

For every object, count the **strong** references after each line: names in the module, slots in
a list, values in a dict, local variables of a running function, attributes of other objects.
The weak references (`ra`, `rc`, ...) do not count. The object dies on the line where its count
reaches zero.

For the last part, draw `x` and `y` as two boxes with arrows. After `del x` and `del y`, which
arrows are left? Who could free the two boxes now that automatic collection is off?

## Hint 2

```
Node "a":  names a, b         -> del a: still b         -> alive; b = new Node: 0 -> dead
Node "c":  name c + 2 slots   -> del c: 2 slots         -> alive
           pop(): 1 slot      -> alive;  clear(): 0     -> dead
Node "d":  one dict value     -> replaced               -> dead
make():    only the local     -> function returns, frame gone -> dead
keep():    local + returned in a tuple -> kept holds it -> alive; kept = None -> dead
x <-> y:   del x: y.other still points at x             -> both alive
           del y: each is held by the other (a cycle)   -> both alive (refcounts are 1, not 0)
           gc.collect(): finds the unreachable cycle    -> both dead, found > 0
```
