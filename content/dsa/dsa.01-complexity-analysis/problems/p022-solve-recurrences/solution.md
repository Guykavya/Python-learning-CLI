The model answer is shown when you check. The ideas that must appear:

1. Master theorem: compare `a` with `b^d` (equal: `n^d log n`; `a` smaller: `n^d`; `a` bigger: `n^(log_b a)`).
2. Answers: 1 O(n log n); 2 O(log n); 3 O(n); 4 O(n^2); 5 O(n); 6 O(n); 7 O(n^2); 8 O(2^n).
3. Matches: binary search 2; two calls on n - 1 is 8; indexed recursive sum 6; merge sort 1.
4. Subtract-by-one recurrences have `n` levels; the master theorem needs division by a constant `b`.
