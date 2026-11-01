## Approach

Every `t.something` (and every `self.something` inside a method, because `self` is `t`) runs
`Tracked.__getattribute__` first. If that raises `AttributeError`, Python calls
`Tracked.__getattr__`. Built-in operations that use special methods (`len`, `repr`) ask the
type directly and never pass through the instance hooks.

## Trace

| Line | What happens | Output |
|---|---|---|
| `t = Tracked()` | `self.size = 3` is a **set**; neither get hook is involved | nothing |
| A | `t.size` is in the instance dict | `get size`, `A 3` |
| B | `color` is nowhere, normal lookup fails | `get color`, `fallback color`, `B <color>` |
| C | `area` is a property, its getter reads `self.width`, which fails and falls back to `"<width>"`; `"<width>" * 2` | `get area`, `get width`, `fallback width`, `C <width><width>` |
| D | the getter raises `AttributeError("broken inside")`, so Python calls `__getattr__("broken")`; the real error is hidden | `get broken`, `fallback broken`, `D <broken>` |
| E | `len(t)` calls `type(t).__len__(t)` directly; only `self.size` inside goes through the hook | `get size`, `E 3` |
| F | `t.__len__` is an explicit dotted lookup, then the body reads `self.size` | `get __len__`, `get size`, `F 3` |
| G | `repr(t)` uses the type's `__repr__` | `G T` |
| H | `_secret` fails, the fallback raises `AttributeError`, `hasattr` turns that into `False` | `get _secret`, `fallback _secret`, `H False` |
| I | `anything` fails, the fallback returns a string, so the attribute "exists" | `get anything`, `fallback anything`, `I True` |
| J | same as H, and `getattr` returns its default | `get _x`, `fallback _x`, `J default` |
| `t.color = "red"` | a set: no get hook | nothing |
| K | `color` is now in the instance dict, no fallback | `get color`, `K red` |
| L | `type(t)` is not an attribute lookup on `t`; `.__name__` is looked up on the **class** | `L Tracked` |

## What to remember

- Line D is the trap of this module: a bug inside a property (`AttributeError` raised by a
  typo) silently turns into a `__getattr__` call. Line C shows the same thing caused by a missing
  attribute: the property "works" and returns nonsense.
- Line I: a `__getattr__` that answers every name makes `hasattr` always `True`. That is why the
  fallback refuses names that start with `_`; tools like `copy` and `pickle` probe dunder names
  with `hasattr`.
- Lines E and G: counting attribute accesses with `__getattribute__` misses everything that
  Python does through the type.

## Another way

Remove `__getattr__` and run it again: lines B, C and D raise `AttributeError` instead, and H
and J still work (they catch the error). Removing `__getattribute__` only removes the `get` lines.
