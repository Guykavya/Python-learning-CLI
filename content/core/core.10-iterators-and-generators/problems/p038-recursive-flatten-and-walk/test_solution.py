from solution import flatten, walk


def test_flatten_basic():
    assert list(flatten([1, [2, [3, [4]]], (5, 6), []])) == [1, 2, 3, 4, 5, 6], (
        "Flatten lists and tuples at every depth. Call flatten on each inner list/tuple and 'yield from' it."
    )


def test_flatten_strings_are_items():
    assert list(flatten(["ab", ["cd", ("ef",)]])) == ["ab", "cd", "ef"], (
        "A string is one item. Only lists and tuples are opened. Do not test 'is it iterable'."
    )


def test_flatten_other_items():
    assert list(flatten([{"a": 1}, [None, 0, [False]]])) == [{"a": 1}, None, 0, False], (
        "dicts, None, 0 and False are ordinary items: yield them, do not drop falsy values."
    )


def test_flatten_empty():
    assert list(flatten([])) == [], "An empty list gives nothing."
    assert list(flatten([[], [[]], ()])) == [], "Empty inner lists give nothing; do not yield the empty lists themselves."


def test_flatten_deep():
    data = [7]
    for _ in range(60):
        data = [data]
    assert list(flatten(data)) == [7], "Depth 60 must work. Recursion handles any depth; a fixed number of loops does not."


def test_flatten_is_a_generator():
    g = flatten([1, [2]])
    assert iter(g) is g, "flatten must return an iterator (a generator), not a list."
    assert next(g) == 1, "The first item is 1."


def test_flatten_is_lazy():
    data = [[1, 2], [3]]
    g = flatten(data)
    assert next(g) == 1, "The first item is 1."
    data[1].append(4)
    assert list(g) == [2, 3, 4], (
        "flatten must be lazy: it reads the data only when items are asked for. "
        "Do not build a full result list first."
    )


TREE = {
    "README.md": 5,
    "src": {"main.py": 120, "lib": {"a.py": 30, "b.py": 7}},
    "empty": {},
}


def test_walk_example():
    assert list(walk(TREE)) == [
        ("README.md", 5),
        ("src/main.py", 120),
        ("src/lib/a.py", 30),
        ("src/lib/b.py", 7),
    ], "Join names with '/', recurse into dicts, keep the dict order, skip empty folders."


def test_walk_no_leading_or_double_slash():
    paths = [p for p, _ in walk({"a": {"b": {"c": 1}}})]
    assert paths == ["a/b/c"], "The path is 'a/b/c': no slash at the start and no double slash."


def test_walk_zero_size_file():
    assert list(walk({"x": 0})) == [("x", 0)], "A file of size 0 is still a file. Check isinstance(value, dict), not truthiness."


def test_walk_empty():
    assert list(walk({})) == [], "An empty tree has no files."


def test_walk_is_lazy():
    tree = {"a": 1, "b": {"c": 2}}
    g = walk(tree)
    assert next(g) == ("a", 1), "The first file is ('a', 1)."
    tree["b"]["d"] = 3
    assert list(g) == [("b/c", 2), ("b/d", 3)], "walk must be lazy: do not collect all files into a list first."
