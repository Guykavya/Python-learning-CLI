class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __repr__(self):
        return f"Book({self.title!r}, {self.author!r})"

    def __str__(self):
        return f"{self.title} by {self.author}"


class Tag:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Tag({self.name!r})"
