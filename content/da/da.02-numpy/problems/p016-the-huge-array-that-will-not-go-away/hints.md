## Hint 1

Is `data[:10]` a view or a copy (Ch. 6.2)? If it is a view, where do its ten numbers physically live? What would happen to those numbers if the big block were freed?

## Hint 2

```text
view  -> no own memory -> holds a reference to its .base (the 1 GB array)
Python frees memory only when the reference count drops to 0
check: part.base is not None, part.flags["OWNDATA"] is False
fix:   data[:10].copy()  -> own 80 bytes, base None -> the big array can be freed
```
