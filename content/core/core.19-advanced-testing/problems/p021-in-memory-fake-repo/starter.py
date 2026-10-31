class UserNotFound(KeyError):
    pass


class DuplicateUser(ValueError):
    pass


class FakeUserRepo:
    def add(self, user_id, name):
        pass

    def get(self, user_id):
        return None

    def delete(self, user_id):
        pass

    def names(self):
        return []
