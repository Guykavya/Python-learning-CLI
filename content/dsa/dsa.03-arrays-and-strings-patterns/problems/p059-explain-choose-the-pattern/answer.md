**1. Best run of days: Kadane.** We want the maximum sum of one contiguous stretch, and losses are negative, so a
window has no "grow or shrink" rule. Kadane keeps the best sum of a run ending today: extend it if the run so far is
not negative, otherwise start again today. O(n) against O(n^2) for trying every start and end (O(n^3) if each sum is
recomputed). **Trap:** if every day is a loss, the answer is the smallest loss, not 0: start `best` at the first day,
not at 0.

**2. Range totals: prefix sums.** The list never changes and there are many queries. Build `P` once (O(n)); each query
is `P[r] - P[l - 1]`, O(1). Total O(n + q) against O(n q) = 2 * 10^9 for summing each range. **Trap:** if orders are
**updated** between queries, a single update changes O(n) prefix values; then you need a Fenwick tree or segment tree
(a later module).

**3. Sorted heights, pair sum: two pointers.** Start at both ends; if the sum is too small, the smallest height cannot
be in any pair with the largest still possible, so move the left pointer; if too big, move the right. O(n), with O(1)
memory, against O(n^2) for all pairs. **Trap:** if the list is **not** sorted, the argument fails: sort first (O(n log n))
or use a set of seen heights (O(n) with O(n) memory).

**4. Shortest stretch with sum at least S: variable sliding window.** All readings are positive, so growing the window
always increases the sum and shrinking always decreases it. Grow `right`; while the sum is at least `S`, record the
length and shrink `left`. O(n), each pointer moves at most `n` times, against O(n^2). **Trap:** if readings can be
**negative** (a temperature change), shrinking can raise the sum and the window breaks; use prefix sums with a monotonic
deque (O(n)).

**5. Seat bookings: difference array.** Many range **updates**, one read at the end. For each booking do
`d[l] += v; d[r + 1] -= v`, then one prefix-sum pass gives every seat's count. O(n + q) against O(n q) = 5 * 10^9 for
adding to every seat of every booking. **Trap:** if someone asks for a seat's count **between** bookings, the difference
array is not ready until the prefix pass; with many interleaved questions you need a Fenwick tree.

**General lesson.** The deciding properties are: contiguous or not, positive or not, sorted or not, fixed or variable
size, many queries or one answer.
