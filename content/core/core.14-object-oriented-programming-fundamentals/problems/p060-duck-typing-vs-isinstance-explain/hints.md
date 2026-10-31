## Hint 1

What does `save` actually **need** from `target`? Write it down in one sentence. Now look at each
version: does it check that need, or something else? Try `type(io.StringIO())` in the REPL.

## Hint 2

For the hidden bug in C, follow one call: `save_c(["hi"], Shout())` -> `target.write("hi\n")` ->
inside `write`, `self.part` -> `AttributeError`. Which `except` catches it? What message does the user
see, and what happened to the real error?

## Hint 3

Plan of the answer:

```text
1. A: file only (exact type); B, C: all three
2. duck typing = needs the behaviour (write), not the class; B and C
3. LBYL = check then act (early, clear error); EAFP = act, catch failure (real behaviour, no double work)
   C's try is too big -> swallows AttributeError from inside write -> keep try around the lookup only
4. exists() then read: the file can vanish in between -> just try and catch FileNotFoundError
5. total: no check, or isinstance(x, collections.abc.Iterable)
   isinstance is right for: str vs list-of-str, validation at a library edge, own exception classes
```
