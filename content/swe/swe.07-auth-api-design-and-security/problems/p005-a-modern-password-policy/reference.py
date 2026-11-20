MIN_LENGTH = 12
MAX_LENGTH = 256


def check_password_policy(password: str, username: str = "", breached=frozenset()) -> list[str]:
    problems = []
    if len(password) < MIN_LENGTH:
        problems.append("too_short")
    if len(password) > MAX_LENGTH:
        problems.append("too_long")
    if password.lower() in breached:
        problems.append("breached")
    if username and username.lower() in password.lower():
        problems.append("contains_username")
    if password and len(set(password)) == 1:
        problems.append("one_character")
    return problems
