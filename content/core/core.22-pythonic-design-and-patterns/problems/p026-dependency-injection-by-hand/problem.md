# Dependency injection by hand

`starter.py` has a `SignupService` that creates its own clock and mailer inside `signup` and
stores users in a **module-level list**. You cannot test it without sending real output and
real time, and two services share one global list.

Rebuild it with **constructor injection** and a **composition root**, with no framework.
Copy `starter.py` to `solution.py` and write these names:

- `SignupError(ValueError)`.
- `User`: a frozen dataclass with `email`, `name`, `created_at` (a `datetime`).
- Clocks: `SystemClock` (`now()` returns `datetime.now()`) and `FixedClock(moment)` (`now()`
  always returns `moment`).
- Mailers (method `send(to, subject, body)`): `ConsoleMailer` prints
  `MAIL to=<to> subject=<subject>`; `InMemoryMailer` keeps `(to, subject, body)` tuples in a
  list attribute `sent`.
- `InMemoryUserRepo` with `exists(email)`, `add(user)` and `get(email)` (returns the `User` or `None`).
- `SignupService(repo, mailer, clock)` that stores them as `self.repo`, `self.mailer`,
  `self.clock`. `signup(email, name)`:
  1. strip and lower-case the email;
  2. it must have exactly one `@`, something before it, and a domain containing a `.`; otherwise `SignupError("invalid email")`;
  3. if `repo.exists(email)`: `SignupError("already registered")`;
  4. build `User(email, name, clock.now())`, `repo.add(user)`, then
     `mailer.send(email, f"Welcome, {name}", <any body>)`;
  5. return the user.
  Nothing may be called on the collaborators when validation fails.
- `build_app(config)` is the **composition root**, the one place that chooses concrete
  classes. If `config.get("env") == "test"` it returns a service with `InMemoryUserRepo`,
  `InMemoryMailer` and `FixedClock(config.get("now", datetime(2024, 1, 1, 12, 0)))`. Otherwise it wires
  `InMemoryUserRepo`, `ConsoleMailer` and `SystemClock`. Each call builds fresh objects.

Rules (checked by the tests): `SignupService` never creates a clock, mailer or repo, never
imports inside its methods, never calls `print` or `datetime.now`; and the module has no
module-level list, dict or set.

**Example**

```python
app = build_app({"env": "test", "now": datetime(2025, 3, 14, 9, 26)})
user = app.signup(" Ana@Example.com ", "Ana")
user.email            # 'ana@example.com'
user.created_at       # datetime(2025, 3, 14, 9, 26)
app.mailer.sent       # [('ana@example.com', 'Welcome, Ana', ...)]
```
