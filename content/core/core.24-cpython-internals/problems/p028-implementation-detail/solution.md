## Approach

The model answer is in `answer.md`. The rule behind it: write code against the **language
specification**, and use your knowledge of CPython only to explain and measure, never to make
code correct.

| Snippet | CPython detail | Guaranteed fix |
|---|---|---|
| A | equal strings are often the same object (interning) | `==` for values; `is` only for singletons |
| B | refcount reaching 0 closes the file at once | `with open(...)` |
| C | `getsizeof` measures one container, in a version-dependent way | limit `len(cache)`, `lru_cache(maxsize=...)`, measure with `tracemalloc` |
| D | set order follows randomised string hashes | `sorted(...)`, or `dict.fromkeys(...)` for first-seen order |

## Check your answer

- For A, did you name interning and give a run-time string (JSON, `input()`, a join, `.strip()`) that makes `is` false?
- For B, did you explain that CPython closes the file *because* the refcount hits zero at the end of the line, and that PyPy's GC does not do that immediately (unflushed data, leaked handles)?
- For C, did you say that `getsizeof` ignores the keys and values, so the limit never triggers with large values, and that the numbers change between versions (and may raise on PyPy)?
- For D, did you mention hash randomisation (`PYTHONHASHSEED`), so the order changes **between runs** even on the same CPython, and that only dicts keep insertion order?
- Does every fix use a documented guarantee (`==`, `with`, `len`/`lru_cache`, `sorted`/dict order)?
- Did you explain how to recognise a guarantee (a rule in the Language Reference or library docs) versus a detail ("CPython implementation detail" notes, or behaviour you only observed)?

## Another way

You can test for this kind of bug instead of only reviewing for it: run the test suite with
`PYTHONHASHSEED=random` several times (catches D), with `python -W error` (turns A's
`SyntaxWarning` into an error), with `python -X dev` (warns `ResourceWarning: unclosed file` for
B), and, if your project allows, once on PyPy.
