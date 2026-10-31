from hypothesis import strategies as st

# These strategies are correct but wasteful: they generate anything and then throw most of it away.
# Rewrite each one so that it BUILDS only valid values. No .filter() and no assume().
even_numbers = st.integers(min_value=-1000, max_value=1000).filter(lambda n: n % 2 == 0)
sorted_lists = st.lists(st.integers(min_value=-50, max_value=50), max_size=10).filter(lambda xs: xs == sorted(xs))
ordered_pairs = st.tuples(st.integers(-100, 100), st.integers(-100, 150)).filter(lambda t: 1 <= t[1] - t[0] <= 50)
multiples_of_1000 = st.integers(min_value=-1_000_000, max_value=1_000_000).filter(lambda n: n % 1000 == 0)
distinct_lists = st.lists(st.integers(min_value=-20, max_value=20), min_size=2, max_size=8).filter(
    lambda xs: len(set(xs)) == len(xs))
