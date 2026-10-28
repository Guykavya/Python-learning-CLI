class TimestampMixin:
    def __init__(self, *, created=0, **kwargs):
        # TODO: store created and updated, then pass the rest on with super()
        pass

    def touch(self, day):
        # TODO
        pass


class OwnerMixin:
    def __init__(self, *, owner, **kwargs):
        # TODO: check owner, store it, then pass the rest on with super()
        pass

    def is_owned_by(self, name):
        # TODO
        return False


class Document(TimestampMixin, OwnerMixin):
    def __init__(self, title, **kwargs):
        # TODO
        pass

    def describe(self):
        # TODO
        return ""


class SharedDocument(Document):
    def __init__(self, title, *, readers=(), **kwargs):
        # TODO
        pass


class Photo(OwnerMixin):
    def __init__(self, path, **kwargs):
        # TODO
        pass


class Note(TimestampMixin):
    def __init__(self, text, **kwargs):
        # TODO
        pass
