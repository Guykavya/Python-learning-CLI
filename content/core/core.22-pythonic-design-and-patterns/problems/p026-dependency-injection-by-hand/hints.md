## Hint 1

List what `signup` needs from the outside world: storage, a way to send mail, and the time.
Which of these should the service *create*, and which should it *receive*? Who then decides
which real classes are used in production and which in tests?

## Hint 2

```
class SignupService:
    __init__(self, repo, mailer, clock): store the three as attributes
    signup(self, email, name):
        email = strip + lower
        if not valid: raise SignupError("invalid email")
        if self.repo.exists(email): raise SignupError("already registered")
        user = User(email, name, self.clock.now())
        self.repo.add(user)
        self.mailer.send(...)
        return user

def build_app(config):                 # the ONLY place with concrete class names
    if config.get("env") == "test": return SignupService(InMemoryUserRepo(), InMemoryMailer(), FixedClock(...))
    return SignupService(InMemoryUserRepo(), ConsoleMailer(), SystemClock())
```

Put the "state" (the dict of users) inside `InMemoryUserRepo.__init__`: each repo gets its own.
For the email check, `email.split("@")` gives exactly two parts when there is one `@`.
