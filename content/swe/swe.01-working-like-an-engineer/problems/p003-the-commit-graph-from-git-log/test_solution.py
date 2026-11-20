from solution import ancestors, merge_commits, parse_graph

LOG = "m2 d e\ne c\nd m1\nm1 b c\nc a\nb a\na\n"


def test_parse_graph():
    g = parse_graph(LOG)
    assert g["a"] == [], "A root commit has no parents: an empty list."
    assert g["c"] == ["a"]
    assert g["m1"] == ["b", "c"], "Keep the order of the parents."
    assert list(g) == ["m2", "e", "d", "m1", "c", "b", "a"], "Keep the order of the lines."


def test_parse_graph_ignores_blank_lines_and_extra_spaces():
    assert parse_graph("\nb  a\n\na\n\n") == {"b": ["a"], "a": []}


def test_merge_commits_two_merges():
    assert merge_commits(parse_graph(LOG)) == ["m2", "m1"], "A merge has two or more parents. Here: m2 and m1."


def test_no_merges_in_a_straight_line():
    assert merge_commits(parse_graph("c b\nb a\na\n")) == []


def test_ancestors_include_the_commit_itself():
    g = parse_graph(LOG)
    assert ancestors(g, "a") == {"a"}, "The commit is its own ancestor; a root has only itself."
    assert ancestors(g, "d") == {"d", "m1", "b", "c", "a"}
    assert ancestors(g, "e") == {"e", "c", "a"}
    assert ancestors(g, "m2") == set("m2 e d m1 c b a".split()), "m2 contains the whole history."


def test_two_paths_to_the_same_commit():
    g = parse_graph("m b c\nb a\nc a\na\n")
    assert ancestors(g, "m") == {"m", "b", "c", "a"}


def test_parent_missing_from_the_log_is_still_an_ancestor():
    g = parse_graph("b a\n")   # shallow clone: a has no line of its own
    assert ancestors(g, "b") == {"b", "a"}, "A parent with no line has no parents of its own; do not crash."


def test_long_history_needs_no_recursion():
    n = 20000
    text = "".join(f"c{i} c{i - 1}\n" for i in range(1, n)) + "c0\n"
    g = parse_graph(text)
    assert len(ancestors(g, f"c{n - 1}")) == n, "A chain of 20000 commits: use a stack, not recursion."
