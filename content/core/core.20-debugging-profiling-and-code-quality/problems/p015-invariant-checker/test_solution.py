import copy

from solution import ledger_problems


def e(id_, date, amount):
    return {"id": id_, "date": date, "amount": amount}


EXAMPLE = [
    e("a1", "2026-03-01", 5000),
    e("a2", "2026-03-04", -7000),
    e("a1", "2026-03-02", 1000),
    e("a3", "2026-03-05", 2500),
]


def test_example():
    assert ledger_problems(EXAMPLE) == [
        "entry 1: balance -2000 is negative",
        "entry 2: duplicate id 'a1'",
        "entry 2: date 2026-03-02 is before 2026-03-04",
        "entry 2: balance -1000 is negative",
    ], (
        "Collect EVERY problem in one pass (do not stop at the first, as assert would), in entry "
        "order, and for one entry in the order: duplicate id, date, balance."
    )


def test_clean_ledger():
    entries = [e("x", "2026-01-01", 100), e("y", "2026-01-02", -100), e("z", "2026-01-03", 0)]
    assert ledger_problems(entries) == [], "A balance of exactly 0 is not negative: report only balance < 0."
    assert ledger_problems([]) == [], "An empty ledger has no problems."


def test_same_date_is_fine():
    entries = [e("x", "2026-01-01", 100), e("y", "2026-01-01", 5)]
    assert ledger_problems(entries) == [], "Two entries on the same day are fine: only an EARLIER date is wrong (<, not <=)."


def test_balance_keeps_every_amount():
    entries = [e("a", "2026-01-01", -50), e("a", "2026-01-02", 20), e("b", "2026-01-03", 40)]
    assert ledger_problems(entries) == [
        "entry 0: balance -50 is negative",
        "entry 1: duplicate id 'a'",
        "entry 1: balance -30 is negative",
    ], (
        "Add every amount to the balance, even for an entry with a duplicate id; the balance is "
        "-30 after entry 1 and +10 after entry 2."
    )


def test_opening_balance():
    entries = [e("a", "2026-01-01", -500), e("b", "2026-01-02", -600)]
    assert ledger_problems(entries, opening=1000) == ["entry 1: balance -100 is negative"], (
        "Start the balance at `opening`, not at 0."
    )
    assert ledger_problems(entries) == [
        "entry 0: balance -500 is negative",
        "entry 1: balance -1100 is negative",
    ], "With the default opening of 0 both entries leave the balance negative."


def test_date_compares_with_previous_entry():
    entries = [
        e("a", "2026-05-10", 1),
        e("b", "2026-05-01", 1),
        e("c", "2026-05-03", 1),
        e("d", "2026-04-30", 1),
    ]
    assert ledger_problems(entries) == [
        "entry 1: date 2026-05-01 is before 2026-05-10",
        "entry 3: date 2026-04-30 is before 2026-05-03",
    ], (
        "Compare each date with the PREVIOUS entry's date (not with the first or the largest "
        "date). Entry 2 (05-03) is after entry 1 (05-01), so it is fine."
    )


def test_years_and_months():
    entries = [e("a", "2025-12-31", 1), e("b", "2026-01-01", 1), e("c", "2025-12-30", 1)]
    assert ledger_problems(entries) == ["entry 2: date 2025-12-30 is before 2026-01-01"], (
        "Compare the whole ISO date string: a new year is later even though its month is smaller."
    )


def test_many_duplicates():
    entries = [e("t", "2026-01-01", 1)] * 3
    assert ledger_problems(entries) == [
        "entry 1: duplicate id 't'",
        "entry 2: duplicate id 't'",
    ], "The first use of an id is fine; every later use is a duplicate."


def test_input_not_changed():
    entries = copy.deepcopy(EXAMPLE)
    ledger_problems(entries)
    assert entries == EXAMPLE, "Do not change the entries (no pop, no sort, no writing a balance into them)."
