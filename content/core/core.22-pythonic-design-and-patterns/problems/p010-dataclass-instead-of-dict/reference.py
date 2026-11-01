from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class Book:
    title: str
    author: str
    year: int

    def __post_init__(self):
        if not self.title:
            raise ValueError("title must not be empty")
        if self.year < 1450 or self.year > 2100:
            raise ValueError("year out of range")

    def describe(self):
        return f"{self.title} by {self.author} ({self.year})"


@dataclass
class Shelf:
    name: str
    books: list = field(default_factory=list)

    def add(self, book):
        self.books.append(book)

    def titles(self):
        return [b.title for b in self.books]

    def sorted_books(self):
        return sorted(self.books)
