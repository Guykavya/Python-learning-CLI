# How `g.greet("Ann")` becomes `greet(g, "Ann")`

**1. Two steps.** `g.greet("Ann")` is an attribute lookup, `g.greet`, followed by a call of
whatever that lookup returns. They are independent: `m = g.greet` then `m("Ann")` does the same.

**2. The lookup.** `g.greet` runs `type(g).__getattribute__(g, "greet")`, which is
`object.__getattribute__`:

- search `type(g).__mro__` (here `Greeter`, `object`) for `"greet"`. It is found in
  `Greeter.__dict__`: a plain function. Is it a **data** descriptor (has `__set__` or
  `__delete__`)? No. A function has only `__get__`, so it is a **non-data** descriptor;
- look in the instance dictionary `g.__dict__` (`{'greeting': 'Hi'}`): no `"greet"`;
- so use the class attribute found earlier. Because it has `__get__`, Python calls
  `Greeter.__dict__["greet"].__get__(g, Greeter)` and returns **that** result, not the function.

**3. What `__get__` returns.** `function.__get__(g, Greeter)` returns a **bound method**
(`types.MethodType`), a small object that remembers two things: `__func__`, the original
function `greet`, and `__self__`, the instance `g`.

**4. The call.** Calling a bound method calls `__func__` with `__self__` put in front of the
arguments: `m("Ann")` becomes `greet(g, "Ann")`. That is where `self` comes from. Inside,
`self.greeting` is `"Hi"`, so the result is `"Hi, Ann!"`.

**5. By hand:**

```python
Greeter.__dict__["greet"].__get__(g, Greeter)("Ann")   # 'Hi, Ann!'
```

**6. Consequences.**

(a) `g.greet is g.greet` is `False` because every lookup calls `__get__` again and builds a
**new** bound-method object. They compare equal (`==` is `True`), since both wrap the same
`__func__` and `__self__`, but they are two objects.

(b) `Greeter.greet` calls `__get__(None, Greeter)`. With no instance, a function returns
**itself**, so you get the plain function and must pass the instance yourself:
`Greeter.greet(g, "Ann")`.

(c) `g.greet = lambda name: "Yo"` stores the lambda in `g.__dict__`. Because the function in
the class is a non-data descriptor, the instance dictionary is checked **before** it is used,
so `g.greet("Ann")` now returns `"Yo"`. The lambda is not bound (it comes from the instance
dict, so nobody calls its `__get__`), which is why it takes only `name`, no `self`. Other
`Greeter` objects are unaffected. With a data descriptor such as a `property`, the class would
have won instead.

**Summary:** methods are not special syntax. A function in a class is a non-data descriptor
whose `__get__` returns a bound method, and the bound method inserts the instance as the first
argument when called.
