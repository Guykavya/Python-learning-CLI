**1. Storage.** A CPython list object holds the number of items and a pointer to a separate
block of memory. That block is a row of **references** (memory addresses), one per item, side by
side. The item objects themselves (ints, strings, other lists) live elsewhere.

**2. Indexing.** All references have the same size, so slot `i` is at
`start + i × size_of_reference`. Python computes that address and reads it directly, whatever
the list's length. O(1).

**3. Append and growth.** If the block has a spare slot, `append` writes the new reference
there: O(1). If the block is full, CPython allocates a **bigger** block, copies all n references
across (O(n)) and frees the old one. The new block has extra spare room, roughly proportional to
the current size, so the next many appends are cheap again. Expensive appends happen rarely,
and the gaps between them grow with the list. If you add up the cost of all copies over n
appends, it is proportional to n, so the **average** per append is constant.

*Amortised* means "averaged over a long sequence of operations". One append may cost O(n), but
any long run of appends costs O(1) each on average, like a yearly fee spread over months.

**4. Inserting at the front.** The references must stay in order, side by side. To put a new one
at slot 0, every existing reference moves one slot to the right: n moves. `pop(0)` shifts
everything left: also n moves. So each is O(n). A loop of n front inserts does
0 + 1 + ... + (n - 1) ≈ n²/2 moves: O(n²). Doubling n doubles the number of inserts and
doubles the average cost of each, so the total is about four times bigger.

**5. Alternatives.** Append at the end and reverse once (`a.reverse()` is O(n)), or build the
list in the order you need. If you truly need fast operations at both ends, use
`collections.deque`, which is designed for that (core.17).

Key ideas to check: array of references; O(1) indexing by address arithmetic; over-allocation
and rare copies; definition of amortised; shifting makes front operations O(n); n² growth.
