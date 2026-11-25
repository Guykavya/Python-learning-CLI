## Walk-through

1. "scaled" (third rule; nothing in rules 1-2): `preprocessing`.
2. "refund" (fourth rule): `target`.
3. "same patient": `duplicates/groups`.
4. "next": `time`.
5. "twice": `duplicates/groups`.
6. "imputed": `preprocessing`.
7. "after" matches the **first** rule: `time`.
8. "selected": `preprocessing`.

## Story 7

A diagnosis code written after the outcome is a **target** leak: the column is a consequence of the result. The rule says `time` because "after" is tested first. Both views describe the same problem (the value is not known at prediction time); a keyword rule cannot tell which explanation is the better one.
