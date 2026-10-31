# Explain: why (a+)+b explodes

A teammate's input validator uses the pattern `(a+)+b`. It is instant on `"aaaab"`, but on a
string of 30 `a`s followed by a `c` the program seems to freeze. Here are timings from one
laptop (your numbers will differ, the **shape** will not):

```text
n (number of a's, then 'c')   (a+)+b      a+b
16                             0.0076 s    0.000003 s
18                             0.0296 s    0.000002 s
20                             0.1135 s    0.000006 s
22                             0.4445 s    0.000007 s
24                             1.8056 s    0.000007 s
```

With 24 `a`s followed by `b` (a string that **does** match), `(a+)+b` takes about 0.00003 s.

In `answer.md` (about 250 to 400 words), explain:

1. **What the engine tries.** Describe in your own words what a backtracking engine does with
   `(a+)+b` on `"aaaac"`. How many different ways are there to split `n` letters `a` into one or
   more non-empty groups? Connect that number to the timings (what happens to the time when `n`
   grows by 2?).
2. **Why the matching input is fast.** Why does `"a" * 24 + "b"` finish at once while
   `"a" * 24 + "c"` does not?
3. **The rewrite.** Give a pattern that matches exactly the same strings as `(a+)+b` and explain
   why it is fast. Also name the Python 3.11+ feature that can stop the backtracking without
   changing what the pattern means.
4. **Spotting it elsewhere.** Give the general shape of dangerous patterns (at least two shapes,
   with an example each), and two defences when the input comes from users.

**Example** of the level of detail expected for one part:

> 2. On the matching string the very first attempt succeeds: `a+` takes every `a` in one group,
> then `b` matches, and a successful match stops the search. Backtracking only happens after a
> failure.
