**1. Who accepts what.** Version A accepts only the real file, because only `open(..., "w")` returns an
`io.TextIOWrapper`. `io.StringIO()` and `Shout()` both have a working `write(text)` method, yet A
raises `TypeError` for them. A checks the *type*, but the function only needs a *behaviour*. Versions B
and C accept all three.

**2. Duck typing.** `save` only ever calls `target.write(str)`. Anything that has such a method is
good enough, whatever its class: if it "quacks" (`write`), it is a duck (a writable target). B and C
use duck typing; A does not. Duck typing is what makes polymorphism in Python so cheap: `Shout` did not
have to inherit from anything.

**3. LBYL vs EAFP.** *Look before you leap* (B) checks first (`hasattr`) and acts after. Advantage:
the error comes before any work is done, with a clear message; nothing is half-written. *Easier to ask
forgiveness than permission* (C) just acts and handles the failure. Advantages: no double work, and it
tests the real behaviour, not just the presence of a name.

C's hidden bug: the `try` block covers **everything**, including the code *inside* `Shout.write`.
If `write` has a typo like `self.part.append(...)`, that raises `AttributeError`, C catches it and
reports "target needs a write() method", which is false and hides the real bug, and `from None` even
removes the original traceback. Keep the `try` as small as the one operation you expect to fail:

```python
try:
    write = target.write          # only this lookup may fail
except AttributeError:
    raise TypeError("target needs a write() method") from None
for line in lines:
    write(line + "\n")            # bugs in write() now show their real error
```

**4. Races.** Between `path.exists()` and `path.read_text()`, another program can delete or rename the
file, so the check can be true and the read still fail. You need the `try` anyway, so the check adds
nothing but a second disk access. Trying directly and catching `FileNotFoundError` is correct in every
case. The same applies to `if key in d: d[key]` versus `try: d[key]`, although for dicts both are fine
in single-threaded code.

**5. When `isinstance` is right.** `total` only needs something it can loop over that gives numbers.
The simplest fix is no check at all: `return sum(numbers)`, which works for lists, tuples, ranges and
generators, and fails with a clear `TypeError` otherwise. If a check is wanted, check the **ability**
with an ABC: `isinstance(numbers, collections.abc.Iterable)` is `True` for all of those, because ABCs
describe behaviour, not a concrete class.

`isinstance` is the right tool when:

- one input type needs **different handling** although it also quacks: `str` is iterable, but a
  function that accepts "one tag or a list of tags" must check `isinstance(tags, str)` first, or it
  will treat `"python"` as six one-letter tags;
- you **validate at the edge** of a library, where a clear early error is worth more than a confusing
  one deep inside (for example `amount` must be an `int`, not a `float`, in a payment API), and when
  you branch on your own class hierarchy (`isinstance(err, TemporaryError)` to decide to retry).

Prefer ABCs (`Iterable`, `Mapping`, `Sequence`) over concrete classes (`list`, `dict`) in those checks.
