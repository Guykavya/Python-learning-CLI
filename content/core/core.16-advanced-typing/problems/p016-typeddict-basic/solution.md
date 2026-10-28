## Approach

`class Movie(TypedDict)` tells the checker: "a `Movie` is a `dict` with exactly the keys `title` (a `str`), `year` (an `int`) and `rating` (a `float`)". Reading `m["year"]` is then known to give an `int`, and a typo like `m["yaer"]` is an error before the program runs. The shape costs nothing at runtime: instances are plain `dict`s, and `Movie(...)` just builds a dict. Python never checks the keys; only the checker does.

`make_movie` returns a dict literal, which the checker verifies against the three fields. `retitle` builds a new dict with `{**movie, "title": new_title}`: unpack the old keys, then override `title`. The checker still sees a full `Movie`.

## Code

```python
from typing import TypedDict


class Movie(TypedDict):
    title: str
    year: int
    rating: float


def make_movie(title: str, year: int, rating: float) -> Movie:
    return {"title": title, "year": year, "rating": rating}


def describe(movie: Movie) -> str:
    return f"{movie['title']} ({movie['year']}) rated {movie['rating']}"


def retitle(movie: Movie, new_title: str) -> Movie:
    return {**movie, "title": new_title}
```

## Complexity

`make_movie`, `describe`: O(1). `retitle`: O(k) for k keys (here a constant 3).

## Another way

`Movie(title=title, year=year, rating=rating)` also works and reads like a constructor (still a dict). The functional syntax `Movie = TypedDict("Movie", {"title": str, ...})` is needed when a key is not a valid identifier (for example `"release-year"`). If you also want methods and attribute access (`movie.title`), use a `dataclass` instead; TypedDict is best for data that arrives as a dict, like parsed JSON.
