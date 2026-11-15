## Hint 1

The first five prices rise: 31, 41, 48, 59, 79. Each new price pops the single pair below it and adds its span. So the spans are 1, 2, 3, 4, 5, and the stack never holds more than one pair. What happens at 20, which is lower than 79?

## Hint 2

At the first `35` the top is `(20, 1)`: `20 <= 35`, pop, span becomes 2. The next top is `(79, 5)`: `79 <= 35` is false, stop. Push `(35, 2)`. Continue the same way for the second `35` and for `60`.
