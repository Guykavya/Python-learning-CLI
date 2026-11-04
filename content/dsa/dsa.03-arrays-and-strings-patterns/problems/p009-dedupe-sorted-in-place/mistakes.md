- Comparing `a[r]` with `a[r - 1]` instead of the last kept value `a[w - 1]`. Here it happens to give the same
  answer, but it breaks as soon as you adapt the idea to "keep at most two copies". Compare with the last value
  **kept**.
- Starting `w` at 1 without checking `n == 0`: printing `1` for an empty array.
- Deleting with `pop` or `del` inside the loop: the indices of later elements shift under your loop, and each delete
  is O(n).
- Using `set(a)`: it loses the order guarantee and is not in place. (For a sorted list, `sorted(set(a))` gives the
  right values, but not by the method this drill is about.)
- Printing the whole list instead of only the first `k` elements.
