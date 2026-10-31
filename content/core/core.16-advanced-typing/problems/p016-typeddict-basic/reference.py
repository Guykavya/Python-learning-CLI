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
