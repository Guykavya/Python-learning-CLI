See the model answer shown when you check. The ideas that must appear:

1. `test_total` compares a value with itself; `test_discount` has no `assert`. A test must compare the result with an independently chosen expected value. Rewrites: `assert total([10, 20, 30]) == 60` and `assert apply_discount(100, 10) == 90`.
2. The test relies on `test_add_one` having run before (shared module-level list). Running it alone gives `len == 1`, so it fails. Fix: create the cart inside each test.
3. When the first assert fails, the later ones never run; and the name says nothing about which case broke. Split into focused tests or parametrize.
4. "Break the code on purpose: does the test fail?" `test_total` stays green whatever `total` returns.
5. Untested inputs; a wrong expected value; tests that pass for the wrong reason.
