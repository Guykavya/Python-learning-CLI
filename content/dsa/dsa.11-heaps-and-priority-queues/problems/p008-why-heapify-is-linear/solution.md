## Approach

Do not start from a formula. Count on the small tree of 15 items: write down how many nodes live at each height and at each depth, multiply, and add. The two sums (11 and 34) already show the whole story: heapify pays the **height**, which is small for the many bottom nodes, and pushing pays the **depth**, which is large for the same nodes. Then say it in words and generalise with the halving counts `n/2, n/4, n/8, ...`.

## Model answer

See `answer.md`.

## What to check

- You gave the numbers 11 and 34 (or your own correct counts) and not only the words.
- You said that `sift_down` goes **down**, so its cost is at most the node's height.
- You explained why the sum stays at most about `n`: the number of nodes halves at every level while the cost per node only grows by one.
- You separated "correct upper bound" from "tight bound" when you answered the friend.
- You did not claim that heap sort is `O(n)`.

## Another way

Check the claim by counting: the chapter has a table of comparisons (`Counted`) for `heapify` against `n` pushes. For `n = 1,000` on descending data it shows 1,982 against 7,987, and for `n = 100,000` it shows 199,978 against 1,468,946. The first number grows like `2n`, the second like `n log n`. You can also write the sum exactly: for a perfect tree of `n = 2**h - 1` nodes the sum of the heights is `n - h`.
