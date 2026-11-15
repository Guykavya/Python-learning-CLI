# Explain: load factor and resizing

A hash table with `m` buckets holds `n` keys. Its **load factor** is `n / m`. Answer in `answer.md`, in your own words, with
small numbers where they help. Aim for 200 to 350 words.

1. **Chain length.** If keys spread evenly, how long is an average chain in a chaining table with load factor `alpha`? What
   does a lookup cost on average, in terms of `alpha`?
2. **Why resize.** What happens to lookups if you never resize and keep inserting `10^6` keys into 16 buckets? Roughly how
   long is a chain?
3. **Why double.** A table doubles when it gets too full. Suppose instead it grew by **one** bucket every time. How much
   work would `n` inserts cost in total, compared with doubling? Explain **amortised O(1)** with numbers (for example inserts
   `1` to `16` starting at size 1).
4. **Open addressing.** Why does an open-addressing table need a **lower** load factor limit than chaining? What happens at
   load factor 1?
5. **Deletion.** Why is deleting from an open-addressing table harder than from a chaining table?

Then read `solution.md` and `answer.md`, and rate your answer.
