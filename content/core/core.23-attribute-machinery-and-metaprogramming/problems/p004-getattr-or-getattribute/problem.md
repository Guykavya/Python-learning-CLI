# Explain: `__getattr__` or `__getattribute__`?

Both hooks have nearly the same name and the same signature, `(self, name)`, and both can make
`obj.something` return whatever you like. They are not interchangeable.

Write `answer.md` (about 200 to 300 words) that answers these four questions:

1. **When is each one called?** Say exactly which reads reach `__getattribute__` and which reach
   `__getattr__`, and how the two are connected.
2. **Which would you choose** for each of these jobs, and why?
   - (a) an object that forwards unknown attribute names to a wrapped object (a proxy);
   - (b) a `Settings` object that returns a default value for names it does not store;
   - (c) logging **every** attribute read on an object, including ones that exist.
3. **Why is `__getattribute__` risky?** Give two concrete dangers, and show the one line that
   correctly gets the normal value from inside it.
4. **What must both hooks do when they cannot supply a value**, and what breaks if they do
   something else?

**Example of the level of detail expected (a different question)**

> *When is `__setattr__` called?* On every assignment `obj.x = v`, including the ones inside
> `__init__`. That is why a `__setattr__` that validates must store the value with
> `object.__setattr__(self, name, v)`: writing `self.x = v` inside it would call it again forever.
