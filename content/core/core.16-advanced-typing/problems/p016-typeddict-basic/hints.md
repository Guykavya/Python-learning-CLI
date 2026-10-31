## Hint 1

A TypedDict class looks like a dataclass: names and types in the body, no values. What must it inherit from? And at runtime, what kind of object do you get when you call `Movie(title=..., year=..., rating=...)`, or when you write a dict literal with the same keys?

## Hint 2

Since a movie is just a dict, `make_movie` can return a dict literal `{"title": title, ...}`. `describe` is an f-string over the three keys. For `retitle`, how can you copy a dict and then change one key? Two ways: `dict(movie)` followed by an assignment, or `{**movie, "title": new_title}`.

## Hint 3

```
class Movie(TypedDict):
    title: str
    year: int
    rating: float

make_movie(t, y, r):   return {"title": t, "year": y, "rating": r}
describe(m):           f"{m['title']} ({m['year']}) rated {m['rating']}"
retitle(m, new):       return {**m, "title": new}
```
