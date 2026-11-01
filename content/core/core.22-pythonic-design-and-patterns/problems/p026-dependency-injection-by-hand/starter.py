from datetime import datetime

_USERS = []   # global state, shared by every service


class SystemClock:
    def now(self):
        return datetime.now()


class ConsoleMailer:
    def send(self, to, subject, body):
        print(f"MAIL to={to} subject={subject}")


class SignupService:
    """Builds its own collaborators, so tests cannot replace them."""

    def signup(self, email, name):
        if "@" not in email:
            raise ValueError("invalid email")
        if any(u["email"] == email for u in _USERS):
            raise ValueError("already registered")
        user = {"email": email, "name": name, "created_at": SystemClock().now()}
        _USERS.append(user)
        ConsoleMailer().send(email, f"Welcome, {name}", "Your account is ready.")
        return user
