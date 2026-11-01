## Approach

The model answer is in `answer.md`. The whole explanation rests on two facts from the chapter:
the attribute lookup order (data descriptors on the type, then the instance `__dict__`, then
non-data descriptors and plain class attributes) and the fact that every function has a
`__get__` method and no `__set__`.

| Step | What happens | Object you get |
|---|---|---|
| `g.greet` | found in `Greeter.__dict__`, not in `g.__dict__`; function is a non-data descriptor | |
| | `greet.__get__(g, Greeter)` | bound method (`__func__=greet`, `__self__=g`) |
| `(...)("Ann")` | `__func__(__self__, "Ann")` | `greet(g, "Ann")` |

## Check your answer

- Did you separate the lookup from the call?
- Did you say *why* the function is a non-data descriptor (only `__get__`)?
- Did you name both attributes of a bound method (`__self__`, `__func__`)?
- Is your by-hand line runnable? Try it in the REPL.
- For 6c, did you say that the lambda is **not** bound, and that a data descriptor would behave
  the other way?

## Another way

You can check every claim in the REPL:

```python
m = g.greet
type(m).__name__, m.__self__ is g, m.__func__ is Greeter.__dict__["greet"]   # ('method', True, True)
import types
types.MethodType(Greeter.__dict__["greet"], g)("Ann")                          # 'Hi, Ann!'
```

`types.MethodType(func, obj)` is exactly what `func.__get__(obj, cls)` builds.
