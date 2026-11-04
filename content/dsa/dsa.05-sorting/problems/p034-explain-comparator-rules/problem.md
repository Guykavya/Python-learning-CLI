# Explain: what makes a valid comparator?

Python 3 sorts with a **key function** (`key=`) by default. A **comparator** `cmp(a, b)` returning negative, zero or positive is turned into a key with `functools.cmp_to_key`.
Answer in `answer.md`, in your own words (200 to 350 words):

1. **Key versus comparator.** Why does Python prefer `key=`? (Think about how many times each function is called.)
2. **Rules.** A comparator must behave like an ordering. State the three rules: *consistency* (`cmp(a, b)` and `cmp(b, a)` have opposite signs), *transitivity*, and *equality as a relation*.
3. **A broken one.** Rock-paper-scissors: `rock < paper`, `paper < scissors`, `scissors < rock`. Which rule fails? What can a sort do with such a "comparator"?
4. **Largest number.** In problem p021 the order is: `a` first if `a + b > b + a`. Why do you not need to prove transitivity for every pair by hand to trust it? Give the idea in one or two sentences.
5. **Negation trick.** Why does `key=lambda x: -x` work for numbers, and why can you not use it for strings? Name one alternative.

Then read `solution.md` and `answer.md`, and rate your answer.
