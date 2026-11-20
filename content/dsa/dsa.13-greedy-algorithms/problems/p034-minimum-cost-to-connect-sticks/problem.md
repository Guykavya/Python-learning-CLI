# Minimum cost to connect sticks

You have sticks of lengths `[2, 4, 3, 6]`. Joining two sticks of lengths `a` and `b` costs `a + b` and gives one stick of length `a + b`. You join until one stick is left. The total cost depends on the **order** of the joins.

This is the same problem as building a Huffman tree (chapter section 13: "the total cost of all joins equals the cost of the tree"). The program below tries two greedy rules: always join the two **smallest** sticks, and always join the two **largest**. For the largest-first rule it uses the trick from dsa.11: `heapq` is a **min**-heap, so it stores the lengths **negated** (`-6` is the smallest entry, so the biggest stick comes out first) and flips the sign back when it pops.

Predict **exactly** what this program prints. Do not run it.

```python
import heapq


def connect(sticks, smallest_first):
    sign = 1 if smallest_first else -1
    heap = [sign * s for s in sticks]
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        a = sign * heapq.heappop(heap)
        b = sign * heapq.heappop(heap)
        total += a + b
        print(f"join {a} + {b} = {a + b}, total {total}")
        heapq.heappush(heap, sign * (a + b))
    return total


print("smallest first")
small = connect([2, 4, 3, 6], True)
print("largest first")
large = connect([2, 4, 3, 6], False)
print("totals:", small, large)
```

Write your answer in `answer.txt`, one printed line per line.

## How to work

1. For each rule, keep the multiset of stick lengths on paper. You do not need to draw the heap's array: only "which two come out next" matters.
2. Each round: take the two sticks the rule picks (the first popped is `a`), write the join line, add the cost to `total`, and put the new stick back.
3. For the largest-first rule, remember that the new long stick goes back into the heap and is picked again at once.

## After you answer

1. Each stick's length is added to the total once for every join it takes part in. In the largest-first run, how many times is the stick of length 2 counted? And in the smallest-first run?
2. Why is joining the smallest first the cheapest possible order? (Hint: the chapter's Huffman proof.)
3. What would the smallest-first total be for `[5, 5, 5, 5]`, and is there an order that does better?
