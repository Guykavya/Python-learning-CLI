## Hint 1

For each tuple, `zip` calls `next()` on its inputs **from left to right**. To build a tuple, it
must get one item from every input. What does it do when one `next()` raises `StopIteration`?

## Hint 2

In the first half, the generator is on the left. When `zip` tries to build the third tuple, it
asks the generator first. Which number has it already taken out, and where does that number go?
