class TimestampMixin:
    def __init__(self, *, created=0, **kwargs):
        self.created = created
        self.updated = created
        super().__init__(**kwargs)

    def touch(self, day):
        if day < self.created:
            raise ValueError("cannot update before creation")
        self.updated = day


class OwnerMixin:
    def __init__(self, *, owner, **kwargs):
        if not isinstance(owner, str) or owner == "":
            raise ValueError("owner must be a non-empty string")
        self.owner = owner
        super().__init__(**kwargs)

    def is_owned_by(self, name):
        return name == self.owner


class Document(TimestampMixin, OwnerMixin):
    def __init__(self, title, **kwargs):
        self.title = title
        super().__init__(**kwargs)

    def describe(self):
        return f"{self.title!r} by {self.owner}, created day {self.created}"


class SharedDocument(Document):
    def __init__(self, title, *, readers=(), **kwargs):
        self.readers = list(readers)
        super().__init__(title, **kwargs)


class Photo(OwnerMixin):
    def __init__(self, path, **kwargs):
        self.path = path
        super().__init__(**kwargs)


class Note(TimestampMixin):
    def __init__(self, text, **kwargs):
        self.text = text
        super().__init__(**kwargs)
