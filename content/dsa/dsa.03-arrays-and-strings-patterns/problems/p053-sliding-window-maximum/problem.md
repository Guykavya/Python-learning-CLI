# Sliding window maximum

For every window of `k` consecutive elements, print its **maximum**.

A window sum can be updated in O(1) (add the new element, subtract the old one), but a maximum cannot: when the
current maximum leaves the window, which element is the new maximum? Calling `max()` on each window is O(n k): 10^10
steps for `n = 200000`, `k = 100000`.

The fix is a **monotonic deque** (`collections.deque`) of **indices**, whose values are decreasing from front to back:

- before adding index `i`, pop from the back every index whose value is `<= a[i]` (they can never be a maximum again:
  `a[i]` is at least as big and stays in the window longer);
- pop from the front if that index has left the window (`<= i - k`);
- the front is then the index of the maximum of the current window.

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line: the `n - k + 1` window maxima, separated by spaces.

## Example

Input:

```
8 3
1 3 -1 -3 5 3 6 7
```

Output:

```
3 3 5 5 6 7
```

| window | max |
|---|---|
| `1 3 -1` | 3 |
| `3 -1 -3` | 3 |
| `-1 -3 5` | 5 |
| `-3 5 3` | 5 |
| `5 3 6` | 6 |
| `3 6 7` | 7 |

## Constraints

- `1 <= k <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Use `input()` without a prompt message.
