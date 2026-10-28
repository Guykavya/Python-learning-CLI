class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    # TODO: __repr__ -> Book('Dune', 'Frank Herbert')
    # TODO: __str__  -> Dune by Frank Herbert


class Tag:
    def __init__(self, name):
        self.name = name

    # TODO: __repr__ only -> Tag('python')   (do NOT write __str__)
