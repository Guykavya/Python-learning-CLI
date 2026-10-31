class Note:
    count = 0
    history = []

    def __init__(self, title, body="", tags=[]):
        self.title = title
        self.body = body
        self.tags = tags
        cleaned = []
        for tag in self.tags:
            tag = tag.strip().lower()
            if tag and tag not in cleaned:
                cleaned.append(tag)
        self.tags[:] = cleaned
        Note.count += 1

    def add_tag(self, tag):
        tag = tag.strip().lower()
        if not tag:
            raise ValueError("a tag cannot be empty")
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        tag = tag.strip().lower()
        if tag not in self.tags:
            raise KeyError(tag)
        self.tags.remove(tag)

    def edit(self, new_body):
        self.history.append(self.body)
        self.body = new_body

    def undo_edit(self):
        if not self.history:
            raise IndexError("nothing to undo")
        self.body = self.history.pop()
