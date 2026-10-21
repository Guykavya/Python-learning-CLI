**A. Linear search.**
Best case: the target is at position 0, one comparison, O(1).
Worst case: the target is last or missing, `n` comparisons, O(n).
Average case: if the target is present and equally likely to be at any position, about `n/2` comparisons, which is
still O(n). "Average" assumes a probability for where the target is; a different assumption gives a different average.

**B. Sorted check.**
Best case: the first pair is out of order (for example `5 1 2 3 ...`), so it stops after one comparison, O(1).
Worst case: the list is sorted (or the only problem is at the very end), so it compares all `n - 1` neighbour pairs,
O(n). Notice that the **worst** case for this code is the answer "yes, sorted".
Average: on random lists, it usually stops very early (a random list is out of order within the first few pairs),
so the average is O(1), but we would still quote O(n) because a sorted input is perfectly legal.

**C. Insertion sort.**
Best case: already sorted. The `while` test fails immediately for every `i`: `n - 1` comparisons, O(n).
Worst case: sorted in reverse. Element `i` moves all the way left, `i` swaps: `1 + 2 + ... + (n - 1) = n(n - 1)/2`,
O(n^2).
Average: on random order each element moves about halfway, `n^2 / 4` swaps, still O(n^2).
So it is excellent on nearly sorted data and bad in general.

**D. Dict lookup.**
Average case: O(1). The key's hash leads straight to its slot, assuming hashes spread the keys evenly, which they do
for normal data.
Worst case: O(n), if many keys have colliding hashes and Python has to check them one by one. This is very rare by
accident (and Python randomises string hashes to make deliberate attacks hard), so in practice we treat dict and
set operations as O(1).
Best case: O(1).

**Which case to use.** Use the **worst case** over all inputs that the constraints allow, because a judge (or a real
user) will eventually send exactly that input: one test at `n = 2 * 10^5` in the worst shape decides whether you pass.
The examples in a statement are small and often friendly, so a fast result on them says nothing about the worst
case. The exceptions are hashing (we use the average, because the worst case is practically impossible by accident)
and amortised costs like `append`, which are guaranteed over any sequence.

Key ideas to check: A best O(1), worst O(n), average ~n/2 = O(n) with an assumption; B best O(1), worst O(n) when sorted;
C best O(n) sorted, worst O(n^2) reversed, average O(n^2); D average O(1), worst O(n) with collisions; analyse the worst
case at the largest n; examples are not evidence.
