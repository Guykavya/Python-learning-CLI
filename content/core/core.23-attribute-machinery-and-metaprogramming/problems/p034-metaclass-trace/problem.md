# Trace: metaclass inheritance and instance creation

This program mixes three rules from the chapter. Work out everything it prints.

Rules you will need (not the answer):

1. **Which metaclass?** A class uses the *most derived* metaclass among the metaclass you give
   and the metaclasses of all its bases. If none of them is a subclass of all the others, the
   class statement raises `TypeError` (a "metaclass conflict") before anything else runs.
2. **Instance creation.** `C(5)` calls `type(C).__call__`. The default `type.__call__` calls
   `C.__new__`, and calls `__init__` **only if** the object returned by `__new__` is an instance of `C`.
3. **Class keywords.** `class C(A, B, prefix="x-")` passes `prefix` to the parent's
   `__init_subclass__`. A subclass that does not pass it gets the default value.

```python
class MetaA(type):
    def __new__(mcls, name, bases, ns, **kw):
        print(f"MetaA.__new__ mcls={mcls.__name__} class={name}")
        return super().__new__(mcls, name, bases, ns, **kw)


class MetaB(MetaA):
    def __call__(cls, *args):
        print(f"MetaB.__call__ {cls.__name__}{args}")
        obj = super().__call__(*args)
        print(f"got {type(obj).__name__}")
        return obj


class A(metaclass=MetaA):
    def __init_subclass__(cls, /, prefix="", **kw):
        super().__init_subclass__(**kw)
        cls.label = prefix + cls.__name__
        print(f"init_subclass {cls.__name__} label={cls.label}")


class B(metaclass=MetaB):
    pass


class C(A, B, prefix="x-"):
    def __new__(cls, n):
        print(f"C.__new__ {n}")
        if n < 0:
            return "negative"
        return super().__new__(cls)

    def __init__(self, n):
        print(f"C.__init__ {n}")
        self.n = n


class D(C):
    pass


class Other(type):
    pass


try:
    class E(A, metaclass=Other):
        pass
except TypeError as e:
    print("E failed:", type(e).__name__)

print(type(A).__name__, type(B).__name__, type(C).__name__, type(D).__name__)
print(C.label, D.label, isinstance(C, MetaA))
c = C(5)
r = C(-1)
print(r, hasattr(r, "n"))
d = D(2)
print(type(d).__name__, d.n, d.label)
```

**Example**: the first line is

```
MetaA.__new__ mcls=MetaA class=A
```

because `A` is created by `MetaA` itself. Notice that `mcls` is the metaclass actually in use,
which is not always `MetaA`, even though the method is defined in `MetaA`.

Write in `answer.txt` all the lines the program prints, in order (22 lines).
