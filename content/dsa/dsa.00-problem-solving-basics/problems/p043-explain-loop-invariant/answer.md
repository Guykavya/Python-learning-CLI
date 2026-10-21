**Loop 1: Euclid.**

*Invariant.* Before and after every pass, `gcd(a, b)` equals the gcd of the two numbers originally read.
The values of `a` and `b` change, but their gcd never does.

*Why it stays true.* One pass replaces `(a, b)` with `(b, a % b)`. Write `a % b = a - q * b` with `q = a // b`.
If `d` divides `a` and `b`, it divides `a - q * b`, so it is a common divisor of `b` and `a % b`.
Going back, if `d` divides `b` and `a % b`, it divides `(a % b) + q * b = a`, so it is a common divisor of `a` and `b`.
The two pairs have exactly the same set of common divisors, so they have the same greatest one.

*Why it stops.* `a % b` is always between 0 and `b - 1`. So each pass the new `b` is strictly smaller than the old `b`,
and never negative. A whole number cannot keep decreasing while staying `>= 0`, so `b` reaches 0 after at most
`b` passes (in practice far fewer).

*Why the answer is correct.* When the loop stops, `b == 0`. The invariant says `gcd(a, 0)` is the gcd of the original
numbers. Every number divides 0, so the common divisors of `a` and 0 are just the divisors of `a`, and the greatest one is
`a` itself. So printing `a` prints the right answer. Example: (252, 105), (105, 42), (42, 21), (21, 0): gcd 21 at every step.

**Loop 2: largest so far.**

*Invariant.* After `k` numbers have been read, `largest` is the biggest of those `k` numbers. It is true at the start
(one number read, `largest` is that number) and each pass keeps it true: the biggest of the first `k + 1` numbers is either
the old biggest or the new `x`, and the `if` keeps whichever is larger.

*Why it stops.* `range(n - 1)` has exactly `n - 1` values, so the loop runs `n - 1` times and ends.

*Why the answer is correct.* When it stops, all `n` numbers have been read, so by the invariant `largest` is the biggest of
all of them.

**Starting at 0.** The changed loop's starting value is not one of the input numbers, so the invariant
"`largest` is the biggest of the numbers read so far" is false before the first pass (zero numbers read, yet
`largest = 0`). The real invariant becomes "`largest` is the biggest of 0 and the numbers read". That only equals
the right answer if some number is `>= 0`. If **every** number is negative, for example `-5`, `-2`, `-9`, no `x` is
greater than 0, `largest` stays 0 and the program prints `0`, a number that was never in the input. The correct answer is `-2`.
Starting from the first number, as the original does, makes the invariant true from the beginning for every input.

**The pattern.** Invariant true at the start, kept true by every pass, the loop stops, and at the stop the invariant
says exactly what we wanted. Those four facts together prove the program correct for all inputs, not just tested ones.

Key ideas to check: gcd(a, b) never changes, with the common-divisor reason using a % b = a - q*b both ways; b strictly decreases and stays >= 0, so the loop stops; gcd(a, 0) = a at the end; largest is the max of the numbers read so far; for loop stops after n - 1 passes; starting at 0 breaks the invariant and fails when all numbers are negative.
