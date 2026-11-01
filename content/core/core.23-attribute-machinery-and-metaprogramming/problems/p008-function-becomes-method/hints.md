## Hint 1

What does Python itself do to turn the function on the class into `acc.deposit`? It calls one
method of the function object, with the instance and its class as arguments. Can you call that
method yourself on any function, even one that is not in a class? Which two attributes does a
bound method keep?

## Hint 2

```
bind(func, obj)       -> func.__get__(obj, type(obj))
method_parts(m)       -> (m.__func__, m.__self__)
rebind(m, other)      -> take m.__func__ and bind it to other the same way as bind
```

`types.MethodType(func, obj)` builds the same object directly.
