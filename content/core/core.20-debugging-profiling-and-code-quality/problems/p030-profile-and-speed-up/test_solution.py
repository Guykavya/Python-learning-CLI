import importlib.util
import time
from pathlib import Path

from solution import build_report

FIXTURES = Path(__file__).parent / "fixtures"


def load_original():
    """The slow program from the problem (fixtures/slow_report.py), used as the yardstick."""
    spec = importlib.util.spec_from_file_location("slow_report", FIXTURES / "slow_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_report


ORIGINAL = load_original()


def read(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


# ---------- the same output ----------

def test_fixture_report_identical():
    got = build_report(read("products.csv"), read("orders.csv"))
    expected = read("expected_report.txt")
    if got != expected:
        got_lines, exp_lines = got.splitlines(), expected.splitlines()
        for i, (g, e) in enumerate(zip(got_lines, exp_lines), start=1):
            assert g == e, f"Line {i} of the report differs.\n  expected: {e!r}\n  got:      {g!r}"
        assert len(got_lines) == len(exp_lines), f"The report has {len(got_lines)} lines, expected {len(exp_lines)}."
        assert got.endswith("\n"), "The report must end with a newline, exactly like the original."
    assert got == expected, "The report must be identical to fixtures/expected_report.txt."


def test_unknown_products_skipped():
    products = "id,name,category,price\nA,Apple,fruit,10\n"
    orders = "order_id,date,product_id,quantity\n1,2025-01-05,A,2\n2,2025-01-06,ZZZ,9\n"
    got = build_report(products, orders)
    assert got == ORIGINAL(products, orders), f"An order for an unknown product id is skipped and counted under 'skipped'. Got:\n{got}"


def test_no_orders():
    products = "id,name,category,price\nA,Apple,fruit,10\n"
    orders = "order_id,date,product_id,quantity\n"
    expected = "SALES REPORT\norders: 0\nskipped: 0\nrevenue: 0\n\nBY MONTH\n\nTOP PRODUCTS\n"
    got = build_report(products, orders)
    assert got == expected, f"With no orders the sections are empty. Expected {expected!r}, got {got!r}."


def test_ties_and_month_order():
    products = "id,name,category,price\nB,Bee,x,5\nA,Ant,x,5\nC,Cat,y,1\n"
    orders = (
        "order_id,date,product_id,quantity\n"
        "1,2025-03-01,B,2\n2,2024-12-31,A,1\n3,2025-01-15,A,1\n4,2025-03-02,C,10\n"
    )
    got = build_report(products, orders)
    assert got == ORIGINAL(products, orders), (
        "Months must be sorted (2024-12 before 2025-01), and A, B and C all earn 10, so they are ranked "
        f"by id: A, B, C. Got:\n{got}"
    )


# ---------- faster than the original ----------

def products_text(n):
    return "id,name,category,price\n" + "".join(f"P{i:05d},Item {i},cat{i % 7},{10 + i % 90}\n" for i in range(n))


def orders_text(rows):
    return "order_id,date,product_id,quantity\n" + "".join(f"{k},{d},{p},{q}\n" for k, (d, p, q) in enumerate(rows, 1))


def check_speed(products, orders, what, where):
    start = time.perf_counter()
    expected = ORIGINAL(products, orders)          # the slow yardstick runs once (about 0.2 to 0.3 s)
    slow = time.perf_counter() - start
    got = build_report(products, orders)
    assert got == expected, f"{what}: your report differs from the original's. Fix correctness first."
    fast = float("inf")
    for _ in range(3):                             # best of up to 3 runs, stop as soon as it is clearly fast
        start = time.perf_counter()
        build_report(products, orders)
        fast = min(fast, time.perf_counter() - start)
        if slow / fast >= 5:
            return
    ratio = slow / fast
    assert ratio >= 5, (
        f"{what}: your build_report is only {ratio:.1f}x faster than the original (needs 5x; with all three hot spots "
        f"fixed it is over 50x). On this input the time goes into {where}. Profile it: "
        "cProfile.run('build_report(p, o)', sort='tottime')."
    )


def test_speed_big_catalog():
    n = 2000
    rows = [(f"2025-03-{1 + k % 28:02d}", f"P{n - 1 - k % 20:05d}", 1 + k % 3) for k in range(1500)]
    check_speed(
        products_text(n), orders_text(rows),
        "2000 products, 1500 orders, one month",
        "FINDING PRODUCTS: find_product walks the whole product list for every order. Index the products "
        "by id in a dict once",
    )


def test_speed_many_months():
    rows = [(f"{2023 + (k % 30) // 12}-{1 + k % 12:02d}-{1 + k % 28:02d}", f"P{k % 10:05d}", 1 + k % 4) for k in range(1200)]
    check_speed(
        products_text(10), orders_text(rows),
        "10 products, 1200 orders over 30 months",
        "THE MONTHLY TOTALS: for every month the original re-reads and re-parses every order (strptime). "
        "Add each order to its month's total in the same single pass",
    )


def test_speed_many_products_sold():
    n = 800
    rows = [(f"2025-05-{1 + k % 28:02d}", f"P{k:05d}", 1 + k % 5) for k in range(n)]
    check_speed(
        products_text(n), orders_text(rows),
        "800 products each sold once",
        "THE RANKING: the original sorts all products again for every product to find its rank. Sort once and "
        "number the result with enumerate (product lookups matter here too)",
    )
