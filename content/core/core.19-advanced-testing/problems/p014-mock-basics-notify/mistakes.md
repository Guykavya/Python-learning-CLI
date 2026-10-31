- A user whose name and email look alike, so the wrong field goes unnoticed.
- `sender.send.assert_called_with(...)` (not "once"): it only looks at the **last** call, so a
  double send passes.
- Checking what was sent but never the return value (or the other way round).
- Creating one `sender` for the whole file: calls from earlier tests leak into later asserts.
  Create a fresh `Mock()` in each test (or in a fixture).
- Testing the blank case without `assert_not_called()`, so a message that is sent anyway is missed.
