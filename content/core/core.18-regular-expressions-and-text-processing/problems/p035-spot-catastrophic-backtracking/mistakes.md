- Saying "the string is long". 25 characters is short; the problem is the number of **ways** to
  match it, not its length.
- Saying regex is "always slow". `a+b` on the same input is instant; the shape of the pattern
  decides.
- Thinking `re` compiles to a machine that cannot backtrack. Python's `re` is a backtracking engine
  (unlike, for example, Google's RE2), so ambiguous patterns can blow up.
- Testing only with strings that match. Exponential time appears on near-misses that fail at the
  very end.
- "Fixing" it with the lazy `(a+?)+b`: lazy changes the order of the attempts, not their number;
  a failing input still tries every split.
- Relying on a timeout: `re` has none. Make the pattern unambiguous or limit the input length.
