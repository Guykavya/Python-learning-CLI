**1. What happened.** `big` is a generator expression, so it is a generator: an iterator that
makes its values on demand and remembers its position. The first `sum(big)` pulls every value
(15 and 18) until the generator raises `StopIteration`. Now it is **consumed**: it has no way to
restart. The second `sum(big)` calls `next()`, gets `StopIteration` at once, and adds up nothing.
The sum of nothing is defined as `0`. `max` of nothing has no sensible answer, so `max` raises
`ValueError`. The list `readings` was never changed; only the generator's position moved.

**2. Why 0 is worse.** A crash tells you at once that something is wrong, and where. A quiet `0`
looks like a real result. It can go into a report or an average and nobody notices for weeks.

**3. Two fixes.**
- Keep a list: `big = [r for r in readings if r > 12]`. Use this when the data is small and you
  need it several times (sum, max, len).
- Make a fresh generator each time, for example a function `def big(): return (r for r in readings if r > 12)`
  and call `sum(big())`, `max(big())`. Use this when the data is huge or comes from a stream, so it
  must not sit in memory; each pass recomputes it.

**4. Rule of thumb.** Use a **list** when you need more than one pass, need `len()` or indexing,
want to sort it, or the data is small. Use a **generator** when you read the data once, when it is
very large or endless, when you may stop early (like `islice` or `any`), or in a pipeline where each
stage hands one item to the next.
