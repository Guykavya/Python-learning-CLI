from solution import merge_kind

G = {"a": [], "b": ["a"], "c": ["b"], "d": ["b"], "e": ["d"]}


def test_diverged_lines_need_a_merge_commit():
    assert merge_kind(G, "c", "e") == "merge", "c and e have both moved on since b: a merge commit is needed."
    assert merge_kind(G, "e", "c") == "merge", "The answer does not depend on which side you stand on."


def test_fast_forward():
    assert merge_kind(G, "d", "e") == "fast-forward", "d is an ancestor of e: git only moves the pointer."
    assert merge_kind(G, "a", "e") == "fast-forward"


def test_already_up_to_date():
    assert merge_kind(G, "e", "d") == "up-to-date", "d is already inside e's history."
    assert merge_kind(G, "c", "a") == "up-to-date"


def test_same_commit_is_up_to_date_not_fast_forward():
    assert merge_kind(G, "c", "c") == "up-to-date", (
        "A commit is its own ancestor. Check 'other is already contained' first.")


def test_graph_with_a_merge_commit():
    g = {"a": [], "b": ["a"], "c": ["a"], "m": ["b", "c"], "x": ["m"], "y": ["c"]}
    assert merge_kind(g, "b", "m") == "fast-forward", "b is a parent of the merge m."
    assert merge_kind(g, "x", "c") == "up-to-date", "c is a parent of m, so it is inside x."
    assert merge_kind(g, "x", "y") == "merge", "y moved on from c; x moved on through the merge."


def test_long_history_needs_no_recursion():
    n = 20000
    g = {f"c{i}": [f"c{i - 1}"] for i in range(1, n)}
    g["c0"] = []
    assert merge_kind(g, "c0", f"c{n - 1}") == "fast-forward"
