# Shortest subarray with sum at least k, negatives allowed

Find the length of the **shortest** non-empty contiguous subarray whose sum is **at least `k`**. Print `-1` if none
exists.

With only positive values this is the shrinking window from earlier in the module. Here values can be **negative**,
and the window breaks: in `2 -1 2` with `k = 3`, no window of length 1 or 2 works, but the whole array does, and a
window that shrinks as soon as its sum drops would never see it.

Use prefix sums `P[0..n]`. A subarray `a[j..i-1]` is good when `P[i] - P[j] >= k`. For each end `i` you want the
**latest** `j` with `P[j] <= P[i] - k`. Keep a deque of candidate start indices with **increasing** prefix values:

- **Front:** while `P[i] - P[front] >= k`, the front gives a good subarray ending at `i`; record its length and pop
  it. (Any later end would only give a longer subarray with that start.)
- **Back:** while `P[back] >= P[i]`, pop the back. (Index `i` is later and has a smaller-or-equal prefix: it is a
  better start for every future end.)
- Then append `i`.

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line: the shortest length, or `-1`.

## Example

Input:

```
3 3
2 -1 2
```

Output:

```
3
```

Prefix sums: `0 2 1 3`. Only `P[3] - P[0] = 3` reaches `k = 3`.

## Constraints

- `1 <= n <= 200000`
- `-10^5 <= a[i] <= 10^5`
- `1 <= k <= 10^9`

Use `input()` without a prompt message.
