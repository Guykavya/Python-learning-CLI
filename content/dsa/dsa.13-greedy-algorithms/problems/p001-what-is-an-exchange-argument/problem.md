# Explain: what is an exchange argument?

A greedy algorithm makes one choice, commits to it, and never looks back. Running it on a few inputs does not prove it right: chapter section 4 shows that "fewest conflicts first" looks fine on small drawings and still fails on a ten-interval input. The **exchange argument** (chapter section 3) is the standard way to prove that a greedy choice is safe.

Write a short explanation (8 to 14 sentences) in `answer.md`, using **activity selection** (choose the most events that do not overlap; an event that ends at 5 and one that starts at 5 do not overlap) as your example. Answer these questions:

1. What two properties must hold for a greedy algorithm to be correct? Which one does the exchange argument prove?
2. For activity selection, let `g` be the event that **finishes first**, and let `O` be **any** optimal schedule whose first event (by end time) is `f`. Why is `end(g) <= end(f)`?
3. Replace `f` by `g` in `O`. Why does nothing collide with `g`? Why is the new schedule **no worse** than `O`?
4. What does this prove about `g`? Why does it **not** say that `O` was wrong?
5. After taking `g`, what problem is left? How does "repeat" (induction) finish the proof for the whole greedy schedule?
6. Try the same swap for the wrong rule "shortest event first" on `[(0, 5), (4, 7), (6, 10)]`. Which step of the argument breaks?

## Example of the level of detail wanted

For question 2, a good sentence is: "`g` finishes first among **all** events, and `f` is one of the events, so `g` cannot finish later than `f`." Name the events, do not only say "greedy is better".

Then compare with the model answer and rate yourself.
