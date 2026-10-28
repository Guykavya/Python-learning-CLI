- Saying "the counter is not reset". Resetting would not help: the problem is that there is one
  counter, not that it is never reset.
- Moving `calls = 0` into `wrapper`. Then it is 0 at the start of every call and always prints 1.
- Using `calls` inside `wrapper` without `nonlocal`. `calls += 1` then raises `UnboundLocalError`.
- Saying "shared state is always a bug". It is fine when the sharing is wanted and visible.
