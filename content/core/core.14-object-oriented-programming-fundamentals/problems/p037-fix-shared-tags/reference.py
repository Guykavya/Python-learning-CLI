class Note:
    count = 0                       # shared on purpose: one counter for the whole class

    def __init__(self, title, body="", tags=None):
        self.title = title
        self.body = body
        self.history = []           # bug 2 fixed: each note gets its own history list
        self.tags = []              # bug 1 fixed: a new list per note, never the caller's list
        for tag in tags or ():
            tag = tag.strip().lower()
            if tag and tag not in self.tags:
                self.tags.append(tag)
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
