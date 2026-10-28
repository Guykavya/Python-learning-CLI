# TypedDict: a dict with a known shape

A `dict[str, object]` can hold anything, so the checker cannot tell `movie["year"]` from
`movie["title"]`. A **TypedDict** says which keys exist and the type of each value. At
runtime it is still a plain `dict`: there is no checking, no extra class: the shape is only for
the checker (and for readers).

In `solution.py` write:

```python
class Movie(TypedDict):
    title: str
    year: int
    rating: float
```

and three functions:

1. `make_movie(title: str, year: int, rating: float) -> Movie`: build and return a movie dict.
2. `describe(movie: Movie) -> str`: text like `"Alien (1979) rated 8.5"`.
3. `retitle(movie: Movie, new_title: str) -> Movie`: a **new** movie dict, equal to the old one
   except for the title. The original must not change.

Import `TypedDict` from `typing`.

The tests use `typing.is_typeddict` and `Movie.__required_keys__`. The classic functional syntax
`Movie = TypedDict("Movie", {...})` also passes.

**Example**

```python
m = make_movie("Alien", 1979, 8.5)     # {'title': 'Alien', 'year': 1979, 'rating': 8.5}
describe(m)                            # 'Alien (1979) rated 8.5'
retitle(m, "Aliens")["title"]          # 'Aliens'
m["title"]                             # 'Alien'   (unchanged)
type(m)                                # <class 'dict'>
```
