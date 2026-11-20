from solution import conflicting_facts

ROWS = [
    {"order": 1, "customer": "c1", "email": "a@x.com"},
    {"order": 2, "customer": "c1", "email": "a@x.com"},
    {"order": 3, "customer": "c2", "email": "b@x.com"},
    {"order": 4, "customer": "c2", "email": "bee@x.com"},
]


def test_the_example():
    assert conflicting_facts(ROWS, "customer", "email") == {"c2": ["b@x.com", "bee@x.com"]}


def test_no_conflict_means_empty_dict():
    assert conflicting_facts(ROWS[:2], "customer", "email") == {}, "Same value on many rows is not a conflict."
    assert conflicting_facts([], "customer", "email") == {}


def test_other_fields_and_several_conflicts():
    rows = ROWS + [{"order": 5, "customer": "c1", "email": "z@x.com"}, {"order": 6, "customer": "c1", "email": "a@x.com"}]
    got = conflicting_facts(rows, "customer", "email")
    assert got == {"c1": ["a@x.com", "z@x.com"], "c2": ["b@x.com", "bee@x.com"]}, (
        "Distinct values in first-seen order; a value that returns later is not added twice.")
    assert conflicting_facts(rows, "email", "customer") == {}, "Each e-mail belongs to one customer only."


def test_the_input_is_not_changed():
    rows = [dict(r) for r in ROWS]
    conflicting_facts(rows, "customer", "email")
    assert rows == ROWS
