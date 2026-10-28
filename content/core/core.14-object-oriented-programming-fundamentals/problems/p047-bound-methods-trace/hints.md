## Hint 1

For every line, ask two questions: **where** does Python find the name (instance `__dict__` or the
class)? And is the thing it finds a function on the class (then `self` is filled in for you) or
something else (then you pass every argument yourself)?

`m = a.greet` stores a bound method. Does a bound method remember the *value* of `a.name` at that
moment, or the object `a` itself?

## Hint 2

Walk through the `wave` part like this:

```text
a.wave = wave          -> a.__dict__ has "wave": a plain function
a.wave("hello")        -> wave("hello")            -> x is a str
a.wave()               -> wave()                   -> missing x -> TypeError
Greeter.wave = wave    -> now the class has it too
b.wave()               -> b has no own "wave" -> class function -> bound -> wave(b)
a.wave(3)              -> a still has its own "wave" -> it wins -> wave(3)
del a.wave             -> a's own one is gone
a.wave()               -> class function, bound -> wave(a)
```

For `Loud`: `c.kind()` gets `cls = Loud`. `self.greeting` is looked up on `c`, then on `Loud`.
Does it matter that `f` came from `Greeter`?
