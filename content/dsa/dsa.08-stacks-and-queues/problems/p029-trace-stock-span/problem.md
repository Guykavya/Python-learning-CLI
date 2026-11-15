# Trace: the stock span stack

The **span** of today's price is the number of consecutive days, ending today and including today, on which the price was **at most** today's price. The chapter's `StockSpanner` (section 9, "Stock span") keeps `(price, span)` pairs on a stack and **merges** the spans of the days it pops.

Predict **exactly** what this program prints. Do not run it.

```python
class StockSpanner:
    def __init__(self):
        self.stack = []                        # (price, span)

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span


s = StockSpanner()
for price in [31, 41, 48, 59, 79, 20, 35, 35, 60]:
    span = s.next(price)
    print(price, span, s.stack)
```

Write your answer in `answer.txt`, one printed line per line, for example `31 1 [(31, 1)]` (the price, its span, then the stack as Python prints a list of tuples).

## How to work

For each price: start with `span = 1`. While the top pair has a price **less than or equal to** today's, pop it and add its span. Then push `(price, span)`. Keep the whole stack on paper; it is short.

## After you answer

1. Check the span of `60` by counting days backwards in the price list. Does it match?
2. Why is `(35, 2)` popped when the second `35` arrives? What would change with `<` instead of `<=`?
3. The stack's prices are always strictly decreasing from bottom to top. Why does that follow from the `while` condition?
