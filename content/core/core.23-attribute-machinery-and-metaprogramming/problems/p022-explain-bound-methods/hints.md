## Hint 1

Split `g.greet("Ann")` into `m = g.greet` and `m("Ann")`. Print `type(m)`, `m.__self__` and
`m.__func__`, and compare `m.__func__` with `Greeter.__dict__["greet"]`. Which method does
every function have that makes it a descriptor? Is that enough to be a *data* descriptor?

## Hint 2

Shape of a full answer:

```
lookup:  type(g).__mro__ -> found function in Greeter.__dict__ (non-data descriptor: only __get__)
         g.__dict__ has no 'greet'
         -> return Greeter.__dict__["greet"].__get__(g, Greeter)
__get__: returns MethodType: __func__ = greet, __self__ = g
call:    m("Ann") -> m.__func__(m.__self__, "Ann") -> greet(g, "Ann")
by hand: Greeter.__dict__["greet"].__get__(g, Greeter)("Ann")
6a new object per lookup; 6b __get__(None, cls) returns the function; 6c instance dict beats non-data
```
