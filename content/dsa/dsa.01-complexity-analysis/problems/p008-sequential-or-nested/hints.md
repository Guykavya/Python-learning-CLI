## Hint 1

Sequential: the first loop runs `n` times, then the second loop runs `n` times. Add them.
Nested: the inner loop runs `n` times for **each** of the `n` outer passes. Multiply.

## Hint 2

In "nested constant", each outer pass does 1 step itself and then 5 more in the inner loop.

## Hint 3

In "shrinking", write down the values `size` takes: 8, 4, 2, 1, then 0 (which stops the loop). The inner loop
runs `size` times for each of them. Add those.
