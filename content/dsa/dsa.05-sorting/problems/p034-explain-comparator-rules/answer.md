**1. Key versus comparator.** A key function is called exactly once per element, then Python compares the keys with its built-in fast comparison. A comparator is called on every comparison, about `n log n` times, and each call goes back into Python code. So `key=` is much faster, and it can never be inconsistent.

**2. Rules.** (a) Consistency: if `cmp(a, b) < 0` then `cmp(b, a) > 0`, and `cmp(a, a) == 0`. (b) Transitivity: if `a < b` and `b < c` then `a < c`. (c) Equality is transitive too: if `a == b` and `b == c` then `a == c`. Together they say that the elements can be lined up in a row.

**3. A broken one.** Rock-paper-scissors fails transitivity: `rock < paper < scissors`, yet `scissors < rock`. There is no line-up that satisfies every pair. The sort will not crash; it will finish and return some order that depends on the algorithm and the input order, so results are unreliable.

**4. Largest number.** The rule `a + b > b + a` is equivalent to comparing the numbers `0.aaaa...` (the decimal fraction obtained by repeating `a` forever) with `0.bbbb...`. Real numbers are ordered, so the rule is automatically transitive. Finding such an equivalent key is the easiest way to be sure.

**5. Negation trick.** For numbers, `-x` reverses the order, so ascending sort of `-x` is descending sort of `x`. Strings cannot be negated. Alternatives: sort by the second key first and use `reverse=True` for one pass, using stability; or use `cmp_to_key`.
