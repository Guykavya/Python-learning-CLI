# Explain: how `obj.method(1)` becomes `func(obj, 1)`

You have written `self` as the first parameter of every method since core.14. Now you know
enough to explain **where `self` comes from**. Nothing in the call `g.greet("Ann")` mentions
`g` twice, yet the function receives it.

```python
class Greeter:
    def __init__(self, greeting):
        self.greeting = greeting

    def greet(self, name):
        return f"{self.greeting}, {name}!"


g = Greeter("Hi")
print(g.greet("Ann"))         # Hi, Ann!
```

Write `answer.md` that explains, **step by step**, what Python does for `g.greet("Ann")`.
Cover these points:

1. The two separate steps in `g.greet("Ann")`: the attribute lookup `g.greet`, then the call.
2. How the lookup finds `greet` (which dictionaries are searched, in what order) and why a
   function stored in a class is a **non-data descriptor**.
3. What `function.__get__(g, Greeter)` returns: what kind of object, and what its `__self__`
   and `__func__` are.
4. What calling that object does with the argument `"Ann"`.
5. Write one line of code that does the same as `g.greet("Ann")` **by hand**, starting from
   `Greeter.__dict__["greet"]`.
6. Use what you explained to answer: (a) why `g.greet is g.greet` is `False`; (b) what
   `Greeter.greet` (on the class) gives and how you call it; (c) what happens after
   `g.greet = lambda name: "Yo"` and why the instance attribute wins here.

About 300 to 450 words. Code snippets are welcome.

**Example of the level of detail expected (a different question)**

> *Why does `len(x)` call `type(x).__len__(x)`?* Built-in operations look up special methods on
> the **type**, not on the instance, so an instance attribute `x.__len__ = ...` is ignored. The
> type's function is found and called with `x` as its first argument.
