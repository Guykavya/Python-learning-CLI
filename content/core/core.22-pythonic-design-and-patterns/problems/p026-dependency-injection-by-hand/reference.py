from dataclasses import dataclass
from datetime import datetime


class SignupError(ValueError):
    pass


@dataclass(frozen=True)
class User:
    email: str
    name: str
    created_at: datetime


class SystemClock:
    def now(self):
        return datetime.now()


class FixedClock:
    def __init__(self, moment):
        self.moment = moment

    def now(self):
        return self.moment


class ConsoleMailer:
    def send(self, to, subject, body):
        print(f"MAIL to={to} subject={subject}")


class InMemoryMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))


class InMemoryUserRepo:
    def __init__(self):
        self._users = {}

    def exists(self, email):
        return email in self._users

    def add(self, user):
        self._users[user.email] = user

    def get(self, email):
        return self._users.get(email)


def _valid_email(email):
    local, at, domain = email.partition("@")
    return bool(local) and at == "@" and "@" not in domain and "." in domain


class SignupService:
    def __init__(self, repo, mailer, clock):
        self.repo = repo
        self.mailer = mailer
        self.clock = clock

    def signup(self, email, name):
        email = email.strip().lower()
        if not _valid_email(email):
            raise SignupError("invalid email")
        if self.repo.exists(email):
            raise SignupError("already registered")
        user = User(email, name, self.clock.now())
        self.repo.add(user)
        self.mailer.send(email, f"Welcome, {name}", f"Hi {name}, your account is ready.")
        return user


def build_app(config):
    if config.get("env") == "test":
        clock = FixedClock(config.get("now", datetime(2024, 1, 1, 12, 0)))
        return SignupService(InMemoryUserRepo(), InMemoryMailer(), clock)
    return SignupService(InMemoryUserRepo(), ConsoleMailer(), SystemClock())
