**1. The rule.** If `a == b` is `True`, then `hash(a)` must equal `hash(b)`. The reverse is not
required: two different objects may share a hash (a *collision*) and are then told apart with `==`.

**2. How a dict or set uses both.** To look up a key, Python first computes `hash(key)` and uses
it to jump straight to one small group of slots (a "bucket"). Only the entries in that bucket are
compared with `==`. The hash is a fast way to narrow the search; `==` is the final judge.

**3. What goes wrong in `Version`.** `hash(self.text)` is the same for equal texts, but here `__eq__`
compares *numbers* (`"1.0" == "1.00"` gives equal versions) while the hash uses the *text*.
`Version("1.0")` and `Version("1.00")` are equal, but their hashes differ. So after
`seen = {Version("1.0")}`, the check `Version("1.00") in seen` computes a different hash, jumps to a
different bucket, never meets the stored object, and says `False`, even though `==` would say `True`.
The set can even hold both, so `len(seen)` is 2 for two "equal" versions.

**4. The fix.** Hash exactly what `__eq__` compares: `hash(self.parts)` where `parts` is the tuple
of numbers. In general: `__hash__` should be built from the same fields as `__eq__`
(`hash((self.a, self.b))`).

**5. Why unhashable by default.** A class that defines `__eq__` without `__hash__` gets
`__hash__ = None`. Python prefers an honest "unhashable" error to a silently wrong lookup, because
the inherited identity hash would break the rule above as soon as value equality is used.
