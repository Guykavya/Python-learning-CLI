- Adding `time.sleep` or a retry: it hides the symptom and slows the suite; the cause remains.
- Marking the test `skip`/`xfail` or deleting it: the checker's buggy versions slip through.
- Fixing the order of the tests (renaming `test_a_`, `test_b_`): order must not matter at all.
- `random.seed(1)` inside a test and still using the global generator: other tests change its state.
  Pass a `random.Random(1)` of your own.
- Asserting the exact list order of `unique_tags`: the function does not promise an order.
- Resetting state only **before** a test and not after: the last test leaves data for the next module.
- Testing the greeting at a single hour: the borders (11/12 and 17/18) are where bugs live.
