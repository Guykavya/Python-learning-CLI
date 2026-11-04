# Explain why two pointers never skip the pair

The two-pointer pair search on a **sorted** array looks almost too simple:

```python
def pair_sum(a, target):          # a is sorted in increasing order
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            return i, j
        if s < target:
            i += 1                # throw away a[i]
        else:
            j -= 1                # throw away a[j]
    return None
```

Every step throws away one element for good, and it never looks back. A brute force would check all
`n * (n - 1) / 2` pairs; this checks at most `n - 1`. So why can it never throw away an element that belongs to a
correct pair? Answer in `answer.md`, in your own words, with small examples. Aim for 250 to 450 words.

1. **The "too small" step.** Suppose `a[i] + a[j] < target`. Explain why `a[i]` cannot be part of **any** pair
   that is still possible (that is, a pair with the other index between `i + 1` and `j`). Use the fact that
   `a[j]` is the largest value still in play.
2. **The "too big" step.** Say the same thing for `a[i] + a[j] > target` and the element `a[j]`.
3. **The invariant.** Write one sentence that is true before every pass of the loop, about where a solution pair
   can still be (if one exists). Explain why the two rules above keep it true, and why the loop cannot run
   past a solution.
4. **Worked example.** Run it by hand on `a = [1, 3, 4, 6, 8, 11]`, `target = 10`. Write each step as
   `i j sum move`. Which pair does it return? Name one pair that was never checked and say why skipping it
   was safe.
5. **When it breaks.** Give a small **unsorted** array where the same code misses an existing pair. Then say
   what changes, if anything, when the array has duplicates (for example `[2, 2, 3]`, `target = 4`).
6. **Cost.** Why is it at most `n - 1` comparisons? What is the total cost if the array arrives unsorted?

Then read `solution.md` and `answer.md`, and rate your answer.
