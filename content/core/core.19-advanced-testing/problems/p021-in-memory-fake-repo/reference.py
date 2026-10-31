class UserNotFound(KeyError):
    pass


class DuplicateUser(ValueError):
    pass


class FakeUserRepo:
    def __init__(self):
        self._users = {}

    def add(self, user_id, name):
        if user_id in self._users:
            raise DuplicateUser(user_id)
        if not name.strip():
            raise ValueError("name must not be blank")
        self._users[user_id] = name

    def get(self, user_id):
        if user_id not in self._users:
            raise UserNotFound(user_id)
        return self._users[user_id]

    def delete(self, user_id):
        if user_id not in self._users:
            raise UserNotFound(user_id)
        del self._users[user_id]

    def names(self):
        return [self._users[user_id] for user_id in sorted(self._users)]
