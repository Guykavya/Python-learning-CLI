from solution import plan_tree


def test_the_example():
    rows = [(2, 0, 0, "SEARCH orders USING INDEX idx (customer_id=?)"),
            (7, 0, 0, "USE TEMP B-TREE FOR ORDER BY"),
            (9, 2, 0, "CO-ROUTINE sub"),
            (12, 9, 0, "SCAN items")]
    assert plan_tree(rows) == ("SEARCH orders USING INDEX idx (customer_id=?)\n  CO-ROUTINE sub\n    SCAN items\n"
                               "USE TEMP B-TREE FOR ORDER BY")


def test_empty_and_single():
    assert plan_tree([]) == ""
    assert plan_tree([(3, 0, 0, "SCAN t")]) == "SCAN t", "No trailing newline."


def test_rows_in_any_order():
    rows = [(12, 9, 0, "SCAN items"), (9, 2, 0, "CO-ROUTINE sub"), (7, 0, 0, "B"), (2, 0, 0, "A")]
    assert plan_tree(rows) == "A\n  CO-ROUTINE sub\n    SCAN items\nB", "A child may come before its parent in the list."


def test_siblings_are_ordered_by_id():
    rows = [(1, 0, 0, "root"), (5, 1, 0, "c5"), (3, 1, 0, "c3"), (4, 1, 0, "c4"), (8, 3, 0, "g8")]
    assert plan_tree(rows) == "root\n  c3\n    g8\n  c4\n  c5"


def test_deep_plan_needs_no_recursion():
    n = 5000
    rows = [(1, 0, 0, "n1")] + [(i, i - 1, 0, f"n{i}") for i in range(2, n + 1)]
    out = plan_tree(rows).split("\n")
    assert len(out) == n and out[-1] == " " * (2 * (n - 1)) + f"n{n}", "A chain of 5000 nodes must not hit the recursion limit."


def test_detail_text_is_kept_as_it_is():
    assert plan_tree([(1, 0, 0, "SEARCH t USING INDEX i (a=? AND b>?)")]) == "SEARCH t USING INDEX i (a=? AND b>?)"
