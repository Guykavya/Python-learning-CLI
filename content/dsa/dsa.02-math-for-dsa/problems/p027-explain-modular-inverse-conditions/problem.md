# Explain when a modular inverse exists

The modular inverse of `a` modulo `m` is a number `x` with `a * x % m == 1`. Answer in `answer.md`, in your own
words, with small examples. Aim for 200 to 400 words.

1. **When does it exist?** State the exact condition on `a` and `m`. Show two examples: one where the inverse exists and
   one where it cannot (check every `x` from 0 to `m - 1` for a small `m`, such as `a = 4`, `m = 10`).
2. **Why that condition?** Explain in two or three sentences why `gcd(a, m) > 1` makes an inverse impossible.
3. **Fermat's method.** For a prime `m`, `a^(m-2) % m` is the inverse (when `a % m != 0`). Which condition on `m` does it
   need? Show by an example that it gives a wrong answer for a composite `m`.
4. **Extended Euclid's method.** What does the extended Euclid algorithm give, and how do you turn that into the
   inverse? Does it need `m` to be prime?
5. **Choose.** For each situation say which method you would use, and why:
   (a) many inverses modulo `10^9 + 7`; (b) one inverse modulo `10^18`, or a modulus that may be composite;
   (c) the modulus is 1.

Then read `solution.md` and `answer.md`, and rate your answer.
