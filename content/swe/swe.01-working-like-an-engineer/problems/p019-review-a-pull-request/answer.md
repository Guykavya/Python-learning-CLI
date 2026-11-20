## Model answer

Thanks for the PR, and nice that `total()` reuses `discount()` instead of repeating the formula.

1. **blocking:** `discount` returns a raw float: `price - price * percent / 100` can give results like `19.989999999999998` for money, and `total` adds many of them, so the error grows. Please round to two decimals at the end (`round(..., 2)`), or compute in cents or with `Decimal`. Also, `percent = 150` gives a negative price; should this raise `ValueError` like `with_tax` could for bad input? Either decision is fine, but it should be explicit.
2. **blocking:** `apply_discount` is renamed to `discount`. The diff fixes `checkout.py`, but any other caller (other modules, other repositories, scripts) breaks with `ImportError`. If it is a public function, keep `apply_discount = discount` for one release with a note in the CHANGELOG, or do the rename in its own PR where reviewers expect it.
3. **blocking:** no tests. A new public function and a changed one need tests for at least: 0 percent, 100 percent, a rounding case such as `discount(19.99, 10)`, and the error case. Without tests I cannot see that the change is safe, and the next refactoring cannot either.
4. **nit:** `d` is not a descriptive name (`reduction`?), and `price*percent/100` has no spaces around `*`; running `ruff format` will fix the spacing. Ignore if the formatter already does it in CI.

Could you also expand the description: *what* problem does this solve and *how* did you test it? A reviewer should not have to guess. Happy to look again after the changes.

**Checklist: your answer should mention**
- [ ] finds the **float / money** problem and proposes rounding, cents or `Decimal`
- [ ] finds the **public rename** (API break) and suggests an alias or a separate PR
- [ ] notes the **missing tests** and names cases to test
- [ ] labels each comment (`blocking`, `suggestion`, `nit`); the **nit is marked as a nit**
- [ ] says **why** and offers a **fix**, not only "this is wrong"
- [ ] kind tone, comments on the code not the person, **something good** is mentioned
