## Model answer

1. **`TRIE`**: many prefix queries on a fixed word list; each costs the prefix length, not 50,000 scans. (A sorted list with `bisect` is just as good here.)
2. **`BUILTIN`**: one plain search; `"ERROR 503" in text` runs in C and is linear in practice.
3. **`KMP`**: a stream; KMP's whole state is one integer, so nothing needs to be stored or re-read.
4. **`KMP`**: the smallest period `p = n - pi[n - 1]` must be `< n` and divide `n` (or the trick `s in (s + s)[1:-1]`).
5. **`RK`**: many patterns of the **same length**: one pass, compare each window's hash with a set of 500 hashes, verify hits.
6. **`MANACHER`**: all palindromes in `O(n)`; expanding around centres is `O(n**2)` on repetitive DNA.
7. **`Z`**: "how much of the reference's beginning matches at each position" is the definition of the Z-function of `reference + text` (capped at its length).
8. **`RK`**: binary search on the length, and test each length with prefix hashes in `O(n)`: `O(n log n)`.

**Why not the tempting alternative (two examples).**

- **Task 5 with `BUILTIN`:** 500 calls of `find` in a loop each scan the whole book, so the book is read 500 times. Rabin-Karp reads it once and checks each window against all 500 words with one set lookup. KMP would also need 500 passes, one per pattern.
- **Task 7 with `KMP`:** the prefix function's state after reading `text[i]` is the longest prefix of the reference that **ends** at `i`. The task asks for the longest prefix that **starts** at `i`, which is what `z[m + i]` gives directly. Rebuilding that from KMP states is possible but roundabout.
- (Also good) **Task 2 with `KMP`:** correct, but slower in Python than the C built-in and more code; nothing about the task needs KMP's special powers.

**Checklist: your answer should mention**
- [ ] task 1 `TRIE` (or sorted list + bisect): many prefix queries
- [ ] task 2 `BUILTIN`: one plain search, do not write an algorithm
- [ ] task 3 `KMP`: **stream**, state is one integer
- [ ] task 4 `KMP`: period `n - pi[n - 1]` that **divides** `n`
- [ ] task 5 `RK`: many patterns of **equal length**, one pass, verify hash hits
- [ ] task 6 `MANACHER`: `O(n)` for all centres
- [ ] task 7 `Z`: "matches **starting at** each position"
- [ ] task 8 `RK`: hashing **plus binary search** on the length
