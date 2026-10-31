**1. What 100% means.** Line coverage counts the lines that ran at least once. Branch coverage is stronger: it also
requires every `if` to have been true at least once and false at least once. Here both are 100%, but both only say
"this code was executed". Neither says "the result was checked against the specification".

**2. Why each bug escapes.**
- `shipping(10, False)` returns 5, not 15. This is a **boundary** bug: the code says `> 10` where the spec says "10 kg or more". The
  `if` has been true (12 kg) and false (2 kg), so its branches are covered, but no test used 10, the one value where `>` and `>=`
  differ. Coverage looks at which way a decision went, not at the values around the border.
- `shipping(12, True)` returns 30, not 20. This is a **combination**: the surcharge is added before the doubling, so it is doubled too. The
  heavy path and the express path each ran, in different tests, but never in the same call. Coverage counts each `if` separately and never asks
  whether the two ran for the same input (a combination of paths is not a branch).
- `shipping(-4, False)` returns 5, not an error. This is **missing code**: there is no `if weight_kg < 0` at all, so there is no line and no branch for
  coverage to mark as unrun. Coverage can only measure code that exists, so it cannot find a rule that nobody wrote.

**3. Tests that would catch them.**
- `assert shipping(10, False) == 15` (and 9 for the other side of the border: `== 5`).
- `assert shipping(12, True) == 20` (base 5 doubled to 10, plus the surcharge 10).
- `with pytest.raises(ValueError): shipping(-4, False)`.

**4. Rule of thumb.** Use coverage in the other direction: **low** coverage is a reliable warning, because the lines that never ran are certainly
untested, so look at them. High coverage proves little. Do not aim for a number. Derive tests from the **specification**: for every rule
test the values on both sides of each border, test the important combinations, and test the error cases the spec promises. Mutation-style
thinking ("if I broke this line, would a test fail?") finds weak tests that coverage calls fine.
