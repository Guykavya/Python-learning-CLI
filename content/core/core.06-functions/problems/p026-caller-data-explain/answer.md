**1 and 2.**

- `f1` prints `[1, 2, 3]`. `lst` and `data` are two names for one list. `lst.sort()` is a
  method that **mutates** that list, so the caller sees it sorted.
- `f2` prints `[3, 1, 2]`. `sorted(lst)` builds a **new** sorted list, and `lst = ...`
  **rebinds** the local name to it. The caller's list was only read.
- `f3` prints `[3, 1, 2]`. `lst = lst[:]` rebinds `lst` to a copy, so the following `append`
  mutates the copy, which is thrown away when the function returns.
- `f4` prints `[3, 1, 2, 4]`. On a list, `+=` is an in-place extend: it **mutates** the shared
  object. (It also rebinds `lst`, but to the same object.)
- `f5` prints `[3, 1, 2]`. `lst + [4]` builds a new list, and `lst = ...` rebinds to it; the
  `sort` then mutates only the new list.

**3. The rule.** Calling a function binds the parameter to the **same object** the caller
passed; nothing is copied. If the function mutates that object (methods like `append`/`sort`,
item or slice assignment, `+=` on a list), the caller sees the change. If it assigns a new object
to the parameter name, only the local name moves and the caller is unaffected.

"By reference for lists, by value for ints" is wrong because every object is passed the same
way. Under true pass-by-reference, `f2`'s `lst = sorted(lst)` would change the caller's variable,
and it does not. Ints only look "passed by value" because they are immutable: no operation can
change an int, so `n += 1` must rebind. The difference is mutability, not the way of passing.

Key ideas to check: one object, two names; mutation vs rebinding decides; after rebinding, the
caller's object is unreachable from the function; `+=` mutates lists; immutability explains ints.
