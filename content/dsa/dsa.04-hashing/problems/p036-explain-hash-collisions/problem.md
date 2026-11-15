# Explain: collisions in string hashing

You use a polynomial hash `H(t) = (v(t0) * B^(k-1) + ... + v(t(k-1))) mod M` to compare substrings. Answer in `answer.md`, in
your own words, with small numbers where they help. Aim for 250 to 400 words.

1. **Why a modulus.** Why do we take everything modulo `M` instead of using the plain polynomial value?
2. **Why collisions exist.** A hash maps infinitely many strings to `M` values. What does that mean for strings that differ but
   hash alike? Give an example from this module (the `ga` / `abc` hash with `B = 31`, `M = 101`).
3. **How many collisions?** You compare `n = 200000` substrings pairwise through a set, and `M = 10^9 + 7`. Using the
   rough estimate "pairs / M", about how many colliding pairs do you expect? What does that say about a single modulus of that size?
4. **The fix.** Name two ways to make a collision much less likely (think of the modulus and of using two hashes), and how
   unlikely each makes it.
5. **Letter values.** Why must `v('a')` be 1 and not 0?
6. **Attacks.** If `B` and `M` are fixed and public, how can someone build two different strings with the same hash? How do you defend
   against it, and what should the program do after a hash match when a wrong answer is not acceptable?

Then read `solution.md` and `answer.md`, and rate your answer.
