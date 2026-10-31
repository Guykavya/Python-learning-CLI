# len() and indexing for your class

`len(x)` calls `x.__len__()` and `x[i]` calls `x.__getitem__(i)`. Give a class these two and it behaves like
a sequence: `for` loops, `list(x)`, `reversed(x)` and negative indexes all work.

Write `Playlist(songs)` in `solution.py`:

- `Playlist(songs)` takes any iterable of song titles and stores them in order (copy them into a list).
- `len(p)` is the number of songs.
- `p[i]` is the song at position `i`; negative positions count from the end; an out-of-range index raises
  `IndexError` (just like a list).
- Because of that, `for s in p`, `list(p)`, `"Song" in p` and `bool(p)` work without extra methods.

**Example**

```python
p = Playlist(["Intro", "Main", "Outro"])
print(len(p))        # 3
print(p[0], p[-1])   # Intro Outro
print(list(p))       # ['Intro', 'Main', 'Outro']
print("Main" in p)   # True
p[3]                 # IndexError
```
