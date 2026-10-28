## Approach

Do the mangling yourself first (chapter section 7), then trace a normal program:

- `Vault` body: `__secret` → `_Vault__secret`, `__pin` → `_Vault__pin`.
- `SubVault` body: `__secret` → `_SubVault__secret`, `__pin` → `_SubVault__pin`.
- The bottom lines are outside any class, so `v.__pin` is the plain name `__pin`.

Line by line:

1. `v._hint` → `under the bed` (one underscore: no renaming).
2. `v.reveal()` → `_Vault__secret` is `"gold"`, `_Vault__pin` is 1234 → `gold / 1234`.
3. `v.__pin` looks for the plain name `__pin`. `v` only has `_Vault__pin` → `AttributeError` → `no __pin`.
4. `v._Vault__pin` → `1234`. The "private" value is easy to reach if you know the rule.
5. `sorted(vars(v))` → `['_Vault__pin', 'owner']` (`_` sorts before lowercase `o`).
6. `s.reveal()`: `reveal` is written in `Vault`, so it reads `_Vault__secret` (gold) and
   `_Vault__pin` (1234, set by `Vault.__init__`) → `gold / 1234`. The subclass's `__secret` and
   `__pin` did **not** overwrite the parent's. That is what mangling is for.
7. `s.own_pin()` is written in `SubVault` → `_SubVault__pin` → `9999`.
8. `sorted(vars(s))` → `['_SubVault__pin', '_Vault__pin', 'owner']` (`S` before `V`).
9. `gold silver`.
10. `v.__pin = 0` creates a **new** attribute literally named `__pin`. `reveal` still reads
    `_Vault__pin` → `gold / 1234 0`.

## Output

```text
under the bed
gold / 1234
no __pin
1234
['_Vault__pin', 'owner']
gold / 1234
9999
['_SubVault__pin', '_Vault__pin', 'owner']
gold silver
gold / 1234 0
```

## Complexity

Not applicable.

## Another way

Run `print(vars(Vault))` and `print(vars(SubVault))` to see the mangled class attribute names. In
real code, prefer one underscore (`_pin`) for "internal". Use two only when you write a class that
others will subclass and you must make sure their attribute names cannot clash with yours.
