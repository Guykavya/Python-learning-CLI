import string
from dataclasses import dataclass

from hypothesis import strategies as st

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@dataclass(frozen=True)
class Point:
    x: int
    y: int


small_ints = st.integers(min_value=1, max_value=100)
usernames = st.text(alphabet=string.ascii_lowercase, min_size=3, max_size=12)
digit_lists = st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=5)
stock = st.dictionaries(
    st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=5),
    st.floats(min_value=0, max_value=100),
    min_size=1,
    max_size=4,
)
points = st.builds(Point, x=st.integers(-10, 10), y=st.integers(-10, 10))
id_or_none = st.one_of(st.none(), st.integers(min_value=1, max_value=999))
weekdays = st.sampled_from(DAYS)
