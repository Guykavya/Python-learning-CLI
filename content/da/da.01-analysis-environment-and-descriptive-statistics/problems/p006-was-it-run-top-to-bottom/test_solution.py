import random

import pytest

from solution import run_order_problems


def nb_from(items):
    cells = []
    for item in items:
        if item == "md":
            cells.append({"cell_type": "markdown", "source": "text"})
        else:
            cells.append({"cell_type": "code", "source": "x", "outputs": [], "execution_count": item})
    return {"cells": cells}


def test_clean_notebook():
    assert run_order_problems(nb_from([1, 2, 3])) == [], "A notebook run with 'Restart and run all' (1, 2, 3) has no problems."
    assert run_order_problems(nb_from([])) == [], "No cells, no problems."


def test_never_run():
    assert run_order_problems(nb_from([None, 1])) == [0], "A cell with execution_count None never ran: report it."


def test_out_of_order():
    assert run_order_problems(nb_from([1, 3, 2])) == [2], "2 was run before the cell above it (3): report the third cell."


def test_compare_with_the_largest_not_the_previous():
    assert run_order_problems(nb_from([5, 3, 4])) == [1, 2], "4 is above 3 but below 5: compare with the largest count seen so far, not only the previous cell."


def test_markdown_cells_count_in_the_index_but_are_never_reported():
    assert run_order_problems(nb_from(["md", 2, "md", 1, "md"])) == [3], "Indexes are positions in nb['cells'], markdown cells included."


def test_none_does_not_reset_the_maximum():
    assert run_order_problems(nb_from([4, None, 3])) == [1, 2], "A never-run cell adds nothing to the maximum: 3 is still below 4."


def test_equal_counts_are_suspicious():
    assert run_order_problems(nb_from([1, 1])) == [1], "Counts must strictly increase: use <= when comparing with the largest."


@pytest.mark.parametrize("seed", range(10))
def test_against_a_slow_version(seed):
    rng = random.Random(seed)
    items = [rng.choice([None, rng.randint(1, 9), "md"]) for _ in range(12)]
    expected = []
    for i, item in enumerate(items):
        if item == "md":
            continue
        earlier = [x for x in items[:i] if x not in ("md", None)]
        if item is None or (earlier and item <= max(earlier)):
            expected.append(i)
    assert run_order_problems(nb_from(items)) == expected, f"Wrong for counts {items}: a cell is suspicious if never run or not above every earlier count."
