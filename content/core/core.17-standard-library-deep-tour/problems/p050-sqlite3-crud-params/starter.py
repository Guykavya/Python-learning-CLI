import sqlite3


class ContactBook:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)

    def add(self, name, email, city=None):
        return 0

    def get(self, contact_id):
        return None

    def find_by_city(self, city):
        return []

    def update_email(self, contact_id, email):
        return False

    def delete(self, contact_id):
        return False

    def count(self):
        return 0

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
