## Hint 1

After sorting the two halves, `left` and `right`, for a fixed `right[j]` the left values that satisfy `x > 2 * right[j]` are a suffix of `left`. Why a suffix?

## Hint 2

Count first: for each `right[j]` in increasing order, move a pointer `i` right while `left[i] <= 2 * right[j]`; then `len(left) - i` left values qualify. Since `right` is sorted, `2 * right[j]` only grows, so the pointer only moves forward and never restarts.

## Hint 3

Then do an ordinary merge of `left` and `right` to hand the sorted list to the parent. Do not combine counting and merging in one loop: the two comparisons use different thresholds.
