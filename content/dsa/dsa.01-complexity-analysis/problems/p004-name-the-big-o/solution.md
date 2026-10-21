The model answer is shown when you check. The ideas that must appear:

1. A is O(n): one pass over `a`.
2. B is O(n^2): about `n^2 / 2` comparisons; the 1/2 is dropped.
3. C is O(log n): halving.
4. D is O(n log n): `n` outer passes, each with a doubling loop of about `log2 n` steps.
5. E is O(n): 100 is a constant, even though it makes the code 100 times slower than A.
6. F is O(n + m): sequential loops add, and two independent sizes keep two letters.
7. G is O(n * m): `x in b` on a list scans the list. With a set it becomes O(n + m).
