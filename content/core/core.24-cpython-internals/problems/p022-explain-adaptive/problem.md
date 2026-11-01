# Explain: the specialising adaptive interpreter

Since Python 3.11, CPython rewrites some of a function's bytecode **while the function runs**
(PEP 659). Here is what `dis` shows for the same tiny function at three moments, on Python 3.14
(other versions show different names, and the exact number of calls needed is a detail):

```python
import dis

def add(a, b):
    return a + b

dis.dis(add, adaptive=True)            # (1) before any call
for i in range(100):
    add(i, 1)
dis.dis(add, adaptive=True)            # (2) after 100 calls with ints
for i in range(200):
    add(i * 1.0, 1.5)
dis.dis(add, adaptive=True)            # (3) after 200 more calls with floats
```

```
(1)   RESUME                   0
      LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
      BINARY_OP                0 (+)
      RETURN_VALUE

(2)   RESUME_CHECK             0
      LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
      BINARY_OP_ADD_INT        0 (+)
      RETURN_VALUE

(3)   RESUME_CHECK             0
      LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
      BINARY_OP_ADD_FLOAT      0 (+)
      RETURN_VALUE
```

Write `answer.md` (about 250 to 350 words) that answers these four questions:

1. **What happened between (1) and (2)?** Explain what a *specialised* instruction is, what it
   assumes, what "warming up" means and where the interpreter keeps the information it needs
   (hint: `CACHE` entries / inline caches).
2. **What happened between (2) and (3)?** What does a specialised instruction do when its
   assumption is false, and what does that cost?
3. **Why do type-stable hot loops benefit**, and what kind of code gets little or no benefit?
   Give one concrete example of each.
4. **How can you observe it, and what are the limits of what you see?** Name the tool, and say
   what is version-dependent, and what this is *not* (compare with a JIT compiler).

**Example of the level of detail expected (a different question)**

> *Why does `dis` show `LOAD_FAST` for parameters but `LOAD_GLOBAL` for `len`?* The compiler
> decides how to load each name when it compiles the function. Parameters and assigned names are
> locals, stored in a fixed array in the frame and loaded by index. `len` is not assigned in the
> function, so it must be looked up at run time, first in the module's globals and then in the
> builtins.
