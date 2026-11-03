import math
from pathlib import Path
import sqlite3

import pytest

import solution

STORE = (Path(__file__).parent / "fixtures" / "store.sql").read_text()

# Expected results were computed independently in Python from the fixture rows (Decimal arithmetic), not from the reference SQL.
EXPECTED = {
    1: [('Atlas of Rivers', 45.0), ('Rust in Practice', 39.5), ('Old Coast Maps', 32.0), ('Star Charts', 28.0),
         ('Data Gardens', 27.5)],
    2: [('Eli Park',), ('Gus Neal',)],
    3: [('Fiction', 5), ('Tech', 5), ('Maps', 3), ('Cooking', 1)],
    4: [('Ola Berg',)],
    5: [('Ben Ito', 250.44), ('Ian Cole', 249.25), ('Hana Sato', 223.97), ('Asha Rao', 204.23), ('Dev Shah', 193.0),
         ('Jo Wren', 176.25), ('Eli Park', 167.0), ('Fay Lund', 165.49), ('Kai Moss', 108.99), ('Cleo Dune', 97.51),
         ('Gus Neal', 0.0), ('Lia Fox', 0.0)],
    6: [('2024-01', 116.5), ('2024-02', 268.25), ('2024-03', 349.21), ('2024-04', 410.22), ('2024-05', 691.95)],
    7: [('Paper Cities', 9), ('Night Trains', 8), ('Quiet Hours', 8)],
    8: [('Asha Rao', 4), ('Ben Ito', 3), ('Dev Shah', 3), ('Cleo Dune', 2), ('Eli Park', 2), ('Hana Sato', 2),
         ('Ian Cole', 2), ('Kai Moss', 2)],
    9: [('Lima', 176.25), ('Oslo', 62.0), ('Pune', 71.83), ('Tokyo', 94.88), ('Unknown', 83.5)],
    10: [('Cooking', 'Cooking Fast', 22.0), ('Fiction', 'The Long Tide', 15.0), ('Maps', 'Atlas of Rivers', 45.0),
         ('Tech', 'Rust in Practice', 39.5)],
    11: [('2024-01', 116.5, 116.5), ('2024-02', 268.25, 384.75), ('2024-03', 349.21, 733.96),
         ('2024-04', 410.22, 1144.18), ('2024-05', 691.95, 1836.13)],
    12: [('Eva Holm', 606.0, 1), ('Mira Chen', 352.46, 2), ('Tom Okoro', 317.5, 3), ('Sam Patel', 309.91, 4),
         ('Lena Ruiz', 250.26, 5)],
}

ORDERED = {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12}      # result order is part of the answer
HINTS = {
    1: "Books with price > 25 (25.00 itself is NOT included), price DESC then title.",
    2: "city IS NULL, not city = NULL.",
    3: "COUNT(*) per category; the Cooking category has only one book.",
    4: "An author with no books: LEFT JOIN books and keep rows where the book is NULL (or NOT EXISTS). Not NOT IN with NULLs.",
    5: "All 12 customers must appear: Lia Fox never ordered and Gus Neal only has a cancelled order (revenue 0). Put the status filter in the LEFT JOIN's ON clause, and COALESCE the sum to 0.",
    6: "Non-cancelled orders only; month = strftime('%Y-%m', ordered); round the SUM to 2 decimals.",
    7: "SUM(qty) per book over non-cancelled orders, three rows, ties by title (Night Trains and Quiet Hours both sold 8).",
    8: "COUNT(DISTINCT month) per customer with HAVING >= 2. Cancelled orders do not count as a month.",
    9: "Average of ORDER totals, not of item lines: first SUM per order (CTE or subquery), then AVG per city. A NULL city shows as 'Unknown'.",
    10: "Most expensive book per category: ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) = 1, or a correlated subquery.",
    11: "Start from the monthly totals of question 6 and add SUM(revenue) OVER (ORDER BY month).",
    12: "SUM revenue per author (books -> authors), then RANK() OVER (ORDER BY revenue DESC). Authors with no sales are absent (inner joins).",
}
WIDTH = {1: 2, 2: 1, 3: 2, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3}


@pytest.fixture(scope="module")
def con():
    c = sqlite3.connect(":memory:")
    c.executescript(STORE)
    return c


def close(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and not isinstance(a, str) and not isinstance(b, str) and math.isclose(a, b, abs_tol=1e-9)
    return a == b


def same_rows(got, want):
    return len(got) == len(want) and all(len(g) == len(w) and all(close(x, y) for x, y in zip(g, w)) for g, w in zip(got, want))


@pytest.mark.parametrize("n", range(1, 13))
def test_question(con, n):
    sql = getattr(solution, f"QUERY_{n}")
    assert "FROM" in sql.upper(), f"QUERY_{n}: select from the tables, do not type the answer."
    try:
        cur = con.execute(sql)
        got = cur.fetchall()
    except sqlite3.Error as e:
        pytest.fail(f"QUERY_{n}: SQLite rejected your query: {e}")
    assert len(cur.description) == WIDTH[n], f"QUERY_{n}: expected {WIDTH[n]} columns, got {len(cur.description)}. Return exactly the columns listed in the statement."
    want = EXPECTED[n]
    if n not in ORDERED:
        got, want = sorted(got, key=repr), sorted(want, key=repr)
    assert same_rows(got, want), f"QUERY_{n}: wrong result. {HINTS[n]}\nexpected: {want}\n     got: {got}"
