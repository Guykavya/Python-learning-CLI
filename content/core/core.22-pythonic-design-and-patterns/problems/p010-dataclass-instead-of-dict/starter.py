# The OLD code: records are plain dicts and helper functions.
# Your job: replace it with the dataclasses Book and Shelf described in problem.md.
# (The old functions are kept below only so you can run and read them. Delete them in your solution.)

class Book:
    pass


class Shelf:
    pass


def make_book(title, author, year):
    if not title:
        raise ValueError("title must not be empty")
    if year < 1450 or year > 2100:
        raise ValueError("year out of range")
    return {"title": title, "author": author, "year": year}


def describe_book(book):
    return book["title"] + " by " + book["author"] + " (" + str(book["year"]) + ")"


def make_shelf(name):
    return {"name": name, "books": []}


def shelf_add(shelf, book):
    shelf["books"].append(book)


def shelf_titles(shelf):
    return [b["title"] for b in shelf["books"]]


def shelf_sorted(shelf):
    return sorted(shelf["books"], key=lambda b: (b["title"], b["author"], b["year"]))
