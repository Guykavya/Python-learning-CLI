**1. Where the items are kept.** `tee` reads from the original iterator only once. Every item it
reads is stored in an internal buffer until **all** the tee iterators have taken it. When `a` reads
items 0 to 4, `tee` pulls them from `count()` and keeps them for `b`. Then `b` gets `0` and `1` from
the buffer, not from `count()`.

**2. Why 400 MB versus 10 MB.** The buffer holds the items between the iterator that is furthest
ahead and the one that is furthest behind. In the first program `sum(big_a)` runs `big_a` to the
end while `big_b` has not moved, so `tee` must store all ten million numbers for `big_b`: that is
hundreds of megabytes. In the second program `zip` takes one item from `big_a` and one from `big_b`
in turn. They never get more than one item apart, so the buffer stays tiny and memory stays flat.

**3. The rule.** `tee` is cheap when the copies are used **side by side** and stay close together
(a "peek ahead by one", `pairwise`, zipping a stream with itself). If one copy runs far ahead of the
others, `tee` stores everything in between, which costs as much as `list()` and is slower. If you
will read one copy fully before the other, just use `list()`.

**4. The original iterator.** After `tee(it)`, the tee iterators own `it`. If I call `next(it)`
myself, that item is taken from the source without going into the buffer, so the tee copies
silently miss it. Use only the tee copies from then on.

**5. Better code.** Here two passes are not needed at all: `total = sum(range(10_000_000))` and
then `first = 0`. In general, either make the data twice (call the generator function again, or
use a `range` which is re-iterable), or compute everything in one pass, or keep a list if the data
truly must be read twice.
