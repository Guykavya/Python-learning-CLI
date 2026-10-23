def find_user(users: dict[str, str], user_id: str) -> str | None:
    return users.get(user_id)


def greeting(users: dict[str, str], user_id: str) -> str:
    name = find_user(users, user_id)
    if name is None:
        return "Hello, guest!"
    return "Hello, " + name + "!"


def shout_name(users: dict[str, str], user_id: str) -> str | None:
    name = find_user(users, user_id)
    if name is None:
        return None
    return name.upper()
