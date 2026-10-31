from hypothesis import strategies as st

even_numbers = st.integers(min_value=-500, max_value=500).map(lambda n: n * 2)
sorted_lists = st.lists(st.integers(min_value=-50, max_value=50), max_size=10).map(sorted)
ordered_pairs = st.tuples(st.integers(-100, 100), st.integers(1, 50)).map(lambda t: (t[0], t[0] + t[1]))
multiples_of_1000 = st.integers(min_value=-1000, max_value=1000).map(lambda n: n * 1000)
distinct_lists = st.lists(st.integers(min_value=-20, max_value=20), min_size=2, max_size=8, unique=True)
