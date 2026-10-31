import typing
from typing import get_type_hints

import solution
from solution import describe, make_movie, retitle


def test_movie_is_a_typeddict():
    Movie = getattr(solution, "Movie", None)
    assert Movie is not None, "Define the class Movie."
    assert typing.is_typeddict(Movie), "Movie must inherit from TypedDict: class Movie(TypedDict)."
    assert get_type_hints(Movie) == {"title": str, "year": int, "rating": float}, "Fields: title: str, year: int, rating: float."
    assert Movie.__required_keys__ == frozenset({"title", "year", "rating"}), "All three keys are required (no total=False)."
    assert Movie.__optional_keys__ == frozenset(), "No key is optional here."


def test_function_hints():
    Movie = solution.Movie
    assert get_type_hints(make_movie) == {"title": str, "year": int, "rating": float, "return": Movie}, "make_movie(title: str, year: int, rating: float) -> Movie."
    assert get_type_hints(describe) == {"movie": Movie, "return": str}, "describe(movie: Movie) -> str."
    assert get_type_hints(retitle) == {"movie": Movie, "new_title": str, "return": Movie}, "retitle(movie: Movie, new_title: str) -> Movie."


def test_make_movie():
    m = make_movie("Alien", 1979, 8.5)
    assert m == {"title": "Alien", "year": 1979, "rating": 8.5}, "A movie has exactly the keys title, year, rating."
    assert type(m) is dict, "At runtime a TypedDict is a plain dict."


def test_describe():
    assert describe(make_movie("Alien", 1979, 8.5)) == "Alien (1979) rated 8.5", "Format: '<title> (<year>) rated <rating>'."
    assert describe(make_movie("Up", 2009, 8.0)) == "Up (2009) rated 8.0", "The rating is printed as the float it is: 8.0."


def test_retitle_changes_only_the_title():
    m = make_movie("Alien", 1979, 8.5)
    r = retitle(m, "Aliens")
    assert r == {"title": "Aliens", "year": 1979, "rating": 8.5}, "Same year and rating, new title."
    assert m["title"] == "Alien", "Do not change the original dict: return a copy."
    assert r is not m, "Return a NEW dict."
