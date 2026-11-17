# Explain: why heapify is `O(n)`

Chapter section 4 builds a heap from a list of `n` items by calling `sift_down` on every parent, from the last parent back to the root. There are about `n / 2` calls, and one call can cost `log n`. Yet the whole build is `O(n)`, not `O(n log n)`.

Write a short explanation (10 to 15 sentences) in `answer.md` that answers:

1. Take a **perfect** heap of 15 items (4 levels, all full). How many nodes have **height** 0, 1, 2 and 3? (The height of a node is the number of levels *below* it: a leaf has height 0, the root here has height 3.) What is the largest total number of swaps that `heapify` can make on it?
2. Now push the same 15 items one by one in the worst order (descending numbers, so that every new item climbs all the way to the root). The **depth** of a node is the number of levels *above* it. How many swaps are made in total? Compare with your answer to question 1.
3. Why does one `sift_down` that starts at a node cost at most the **height** of that node, and not `log2(n)`?
4. Using the numbers `n/2` leaves (cost 0), `n/4` nodes of height 1, `n/8` nodes of height 2, and so on, explain why the total is at most about `n` and not `n log n`.
5. Explain in a sentence why the same argument does **not** work for `n` pushes. Which of the two numbers, height or depth, does a push pay, and where do most nodes live?
6. A friend says: "heapify makes `n / 2` calls of `O(log n)`, so it is `O(n log n)`". Is the friend wrong, or only not precise? What is the difference between an upper bound and a tight bound here?
7. Heapify is `O(n)`. Does that make **heap sort** `O(n)`? Why not?

Use chapter section 4 ("Why `O(n)` and not `O(n log n)`?" and the table of counted comparisons). Then compare with the model answer and rate yourself.
