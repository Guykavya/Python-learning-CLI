**`is` versus `==`.** `a == b` asks whether two objects have equal **values** (it calls the
type's equality method, so `1 == 1.0` is `True`). `a is b` asks whether two names refer to the
**same object**, which is the same as `id(a) == id(b)`.

**Why 256 and 257 differ.** CPython, the standard implementation, creates the ints from -5 to 256
once at start-up and reuses them, because they are used so often. Every `256` you write is that
one shared object, so `a is b` is `True`. `257` is not cached: each line in the REPL is compiled
separately and makes its own int object, so the two names refer to two different objects with
equal values.

**Why the conclusion is wrong.**
1. The cache is an implementation detail. The language does not promise it; other implementations
   (PyPy and others) or future versions may behave differently.
2. Even in CPython, results change with context: in a script, both `257` literals in one file can
   be merged into one constant, so `a is b` may be `True`. Results computed at run time, such as
   `int("257")`, give new objects.
3. The question being asked is "are these equal?", which is exactly what `==` answers.
   Using `is` gives code that works in tests and fails later with other values.

**The warning.** Comparing with a literal using `is` is almost always a bug where `==` was meant,
so since Python 3.8 the compiler emits a `SyntaxWarning`.

**When to use `is`.** For singletons, where there is guaranteed to be only one object:
`x is None`, `x is not None`, and occasionally `flag is True`. Also when you really care about
identity, for example checking whether two names refer to the same mutable object
(`a is b` before modifying a shared list), and in type checks like `type(x) is int`.

Key ideas to check: identity vs equality; small-int cache -5..256; implementation detail;
context-dependent results; SyntaxWarning for literals; use `is` for None and identity only.
