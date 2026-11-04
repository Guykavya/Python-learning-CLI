# Why does trial division stop at the square root?

Trial division asks, for `i = 2, 3, 4, ...`: does `i` divide `n`? Programs stop at `i * i > n` instead of going
up to `n - 1`. Explain **why that is safe**. Write your answer in `answer.md` (a paragraph or two).

Your answer should cover:

1. Why does a composite `n` always have a divisor `a` with `a * a <= n`? Use the factor pair `n = a * b`.
2. Using that, why can the loop stop as soon as `i * i > n`, and report "prime"?
3. Use `n = 91` (`7 * 13`) and `n = 97` as examples. What `i` is the last one tried for each, and why does 91 not
   need to test 13?
4. How much work does this save for `n = 10^12`? Compare the number of `i` values with and without the rule.
5. In the loop `while i * i <= n`, why is `<=` needed? Give a number where `<` gives a wrong answer.
6. One related question: in the sieve, why can the crossing of multiples of `p` start at `p * p`?
