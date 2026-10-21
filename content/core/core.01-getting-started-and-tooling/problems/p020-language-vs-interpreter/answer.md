**1. Language vs implementation.** The language is the set of rules (grammar
and meaning) described in the Python Language Reference. CPython is one program,
written in C, that implements those rules; it is the official, most-used one.
PyPy is another implementation with a JIT compiler, often much faster for long
running pure-Python code. MicroPython runs on microcontrollers.

**2. Two stages.** First CPython reads the source text, checks the grammar and
compiles it into bytecode: simple instructions like `LOAD_NAME`, `CALL`,
`STORE_NAME`. Then the evaluation loop (the virtual machine) executes the
bytecode instructions one by one. `dis.dis` shows the bytecode. The compiler can
even pre-compute things like `1 + 2` (constant folding).

**3. The two files.** The missing bracket is a grammar error, found while
compiling, before any line runs: `SyntaxError`, no output. The `pirnt` typo is
valid grammar (a name followed by a call), so compiling succeeds, line 1 runs and
prints, and only when line 30 executes does the name lookup fail with
`NameError`.

**4. `__pycache__`.** When a module is imported, CPython saves its compiled
bytecode as a `.pyc` file there (named with the version, like
`x.cpython-314.pyc`), so later imports can skip compiling if the source has not
changed. It is a cache: safe to delete, recreated automatically, and should be
in `.gitignore`, not committed.

**5. Versions.** 3 = major (huge breaking changes, Python 2 to 3), 14 = minor
(a yearly feature release), 4 = micro (bug and security fixes only). New minor
versions add features (syntax, functions); code using them fails on older
versions, often with a `SyntaxError` or `AttributeError`. Old code usually keeps
working because Python avoids breaking changes within major version 3 (with
deprecations given years of warning).

Key ideas to check: language vs implementation; CPython/PyPy; compile to
bytecode then the evaluation loop executes it; syntax errors at compile time vs
NameError at run time; `.pyc` is a cache, delete-safe, not committed;
major.minor.micro and forward/backward compatibility.
