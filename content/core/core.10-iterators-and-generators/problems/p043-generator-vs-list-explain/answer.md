**1. Size.** The list comprehension runs at once and stores one million references, about 8 bytes
each, so the list object is about 8 MB. The generator stores no items. It only stores its paused
state: the code, the current position in `range`, and its local variables. That is why it is about
200 bytes, and it would be **the same size** for `range(1_000_000_000)`. `getsizeof` even
under-counts the list: it measures only the table of references, not the one million `int` objects
it points to, which take many more megabytes.

**2. Why 0.** A generator is an iterator, so it can be read only once. The comparison on line 3
called `sum(squares_gen)` and used it up. On line 4 the generator is finished, `sum` of nothing is
`0`. The list is unchanged by `sum`, so it can be summed again and again.

**3. What only a list can do.** `len(squares_list)`; indexing like `squares_list[10]` and slicing;
looping over it many times; sorting or changing it in place; checking `x in squares_list` more
than once. A generator gives each item once, in order, and then it is finished.

**4. The rule.** Use a **generator** when the data is big or endless, when you read it once from
start to end, and when you may stop early (so the rest is never computed). Example: a pipeline that
reads a huge log stream, filters error lines and counts them. Use a **list** when you need the data
more than once, need its length or random access, or the data is small. Example: a menu of options
shown to the user many times, or results you will sort. A common pattern is to keep the pipeline
lazy and call `list()` only on the small final result.
