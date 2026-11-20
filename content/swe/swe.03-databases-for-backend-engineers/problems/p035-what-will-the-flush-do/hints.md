## Hint 1

The session already tracks these three groups. What are the attribute names? (They are in the title of the problem.)

## Hint 2

They are collections of **objects**, not names. Turn each into a sorted list of `obj.name`.

## Hint 3

```text
return {"new": sorted(o.name for o in session.new), "dirty": ..., "deleted": ...}
```
