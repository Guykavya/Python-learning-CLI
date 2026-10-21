**A. O(1) extra space, O(n) time.** One variable `total`, whatever `n` is.

**B. O(n) extra space, O(n) time.** It builds a new list with one entry per element.

**C. O(n) extra space at a time, but O(n^2) time.** `rest[1:]` **copies** every element except the first into a new
list. The old copy is thrown away, so only about `n` elements are stored at any moment: O(n) space. But the copies
cost `(n - 1) + (n - 2) + ... + 0`, about `n^2 / 2` element copies: O(n^2) time. Using an index `i` from 0 to
`n - 1` instead does the same in O(n) time and O(1) space.

**D. O(n^2) extra space and time.** `n` rows of `n` zeros. For `n = 10^4` that is 10^8 entries, about 800 MB of
pointers: too much for most machines even though each entry is "just a 0".

**E. O(1) extra space, O(n) time.** `x % 10` has only 10 possible values (0 to 9 for non-negative numbers, and
the same 10 for negative ones in Python), so the set never holds more than 10 items, however big `n` is.

**F. O(n) extra space, O(n) time.** It looks like it uses no memory, but each call waits for the next one to
return before it can add `a[i]`. So all `n + 1` calls are open at once, and each open call keeps its own `a`, `i`
and place to return to (a "frame" on the call stack). Space is proportional to the recursion depth: O(n).

**Why F crashes.** Python limits how deep the call stack may grow (about 1000 calls by default) to protect
against runaway recursion. Snippet F needs a depth of `n + 1`, so `n = 5000` exceeds the limit and raises
`RecursionError`. Snippet A keeps one variable and loops: no calls pile up, so it is O(1) space and works for any
`n`. Recursion depth is a space cost, and in Python it has a hard ceiling.

Key ideas to check: A O(1); B O(n); C O(n) space but O(n^2) time because slicing copies; D O(n^2); E O(1) because at
most 10 keys; F O(n) because n frames are open on the call stack; Python's recursion limit (about 1000) causes the
crash; a loop uses O(1) space.
