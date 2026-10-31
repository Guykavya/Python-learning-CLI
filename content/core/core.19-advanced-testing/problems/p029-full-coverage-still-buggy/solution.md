## Approach

Coverage measures **execution**, not **correctness**. Three kinds of bug stay invisible to it:

1. **Wrong boundary.** The `if weight_kg > 10` decision went both ways in the tests, so its branches count as covered. Coverage never looks at the values
   near the border. Only a test at exactly 10 (and 9) can separate `>` from `>=`.
2. **Paths never combined.** Each `if` ran true and false, but the heavy path and the express path never met in one call. Bugs that depend on the *order* or
   *interaction* of two features need a test that uses both.
3. **Missing code.** A missing check leaves no line to mark. Coverage can say nothing about code that does not exist.

See `answer.md` for the full model answer.

## Complexity

Not applicable. Writing the three extra tests costs one minute; the point is to choose them from the specification, not from the coverage report.

## Another way

Run a mutation tool (such as `mutmut`, a separate program) or do it by hand: change `> 10` into `>= 10`, flip the `*=` and the `+=`, delete a line, and check
that some test fails each time. A mutant that survives points at exactly the missing test. That is what the "write the tests" problems in this module do for you.
