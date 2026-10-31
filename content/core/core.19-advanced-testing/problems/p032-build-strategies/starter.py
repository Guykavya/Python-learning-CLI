import string
from dataclasses import dataclass

from hypothesis import strategies as st

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@dataclass(frozen=True)
class Point:
    x: int
    y: int


# Replace each strategy by one that matches the description in problem.md.
small_ints = st.integers()
usernames = st.text()
digit_lists = st.lists(st.integers())
stock = st.dictionaries(st.text(), st.integers())
points = st.builds(Point, x=st.integers(), y=st.integers())
id_or_none = st.integers()
weekdays = st.text()
