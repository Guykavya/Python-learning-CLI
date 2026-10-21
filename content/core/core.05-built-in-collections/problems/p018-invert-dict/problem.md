# Invert a dictionary

Read `n`, then `n` lines of `key value` (both are words). Store them in a dict in that order.
If a key repeats, the later value replaces the earlier one (the key keeps its first position).

Then **invert** the dict with a dict comprehension so that each value maps to its key, and
print the inverted dict one pair per line:

```
<value> -> <key>
```

When several keys share the same value, only one can survive in the inverted dict: the one that
comes **last** in the original dict. The inverted pairs are printed in the order the
comprehension creates them.

**Example**

Input:
```
4
apple red
banana yellow
cherry red
lime green
```
Output:
```
red -> cherry
yellow -> banana
green -> lime
```
