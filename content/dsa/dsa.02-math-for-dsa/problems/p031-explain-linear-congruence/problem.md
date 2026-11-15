# Explain the linear congruence `a x = b (mod m)`

A *linear congruence* asks for all `x` in `0..m-1` with `a * x % m == b % m`. Answer in `answer.md`, in your own words,
with examples. Aim for 200 to 400 words.

1. **When is there a solution?** State the condition using `g = gcd(a, m)`. Test it on `6x = 4 (mod 10)` and on
   `4x = 3 (mod 8)` by trying every `x`.
2. **How many solutions?** When there is a solution, how many values of `x` in `0..m-1` solve it? Where are they
   on the number line (what is the spacing)?
3. **How do you solve it?** Describe the steps: divide by `g`, find an inverse, build the smallest solution, then list
   the others. Use `6x = 4 (mod 10)` as the worked example.
4. **Special cases.** What happens when `g = 1`? When `a = 0`? When `m = 1`?
5. **Connection.** How does the modular inverse (`a x = 1 (mod m)`) fit into this? Which `b` is it a special case of?

Then compare with `solution.md`.
