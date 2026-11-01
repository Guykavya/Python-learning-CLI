import ast
from pathlib import Path

import solution
from solution import DictCache, NullCache, NullLogger, order_total, price_order_lines

ORDERS = [("pen", 3), ("lamp", 1), ("pen", 2)]


class ListLogger:
    def __init__(self):
        self.records = []

    def info(self, message):
        self.records.append(("info", message))

    def error(self, message):
        self.records.append(("error", message))


class CountingCache:
    def __init__(self):
        self.data, self.hits, self.misses = {}, 0, 0

    def get_or_compute(self, key, compute):
        if key in self.data:
            self.hits += 1
        else:
            self.misses += 1
            self.data[key] = compute()
        return self.data[key]


def test_defaults_work_without_any_collaborator():
    assert order_total(ORDERS) == 3 * 2 + 30 + 2 * 2, "With default logger and cache the total is 6 + 30 + 4 = 40."
    assert price_order_lines(ORDERS) == [("pen", 3, 6), ("lamp", 1, 30), ("pen", 2, 4)], (
        "Each line is (sku, qty, price * qty), in the order of the input."
    )
    assert order_total([]) == 0, "No orders cost 0."


def test_unknown_sku_is_skipped():
    assert order_total([("pen", 1), ("sofa", 4)]) == 2, "Unknown SKUs are skipped, not charged and not a crash."
    assert price_order_lines([("sofa", 1)]) == [], "An unknown SKU produces no line."


def test_null_logger_does_nothing(capsys):
    logger = NullLogger()
    assert logger.info("hello") is None and logger.error("oops") is None, "NullLogger methods return None."
    order_total(ORDERS, logger=logger)
    out = capsys.readouterr()
    assert out.out == "" and out.err == "", "NullLogger must not print anything."


def test_null_cache_always_computes():
    cache = NullCache()
    calls = []

    def compute():
        calls.append(1)
        return 7

    assert cache.get_or_compute("k", compute) == 7, "NullCache.get_or_compute must return compute()."
    assert cache.get_or_compute("k", compute) == 7 and len(calls) == 2, (
        "NullCache never stores anything, so compute runs every time."
    )


def test_real_logger_receives_messages_in_order():
    logger = ListLogger()
    order_total([("pen", 3), ("sofa", 1), ("book", 2)], logger=logger)
    assert logger.records == [
        ("info", "priced pen x3"),
        ("error", "unknown sku sofa"),
        ("info", "priced book x2"),
        ("info", "total 30"),
    ], f"Log records were {logger.records}. Messages must be the same as in the old code."


def test_real_cache_is_used():
    cache = CountingCache()
    assert order_total(ORDERS, cache=cache) == 40, "A cache must not change the result."
    assert (cache.misses, cache.hits) == (2, 1), (
        f"Expected 2 misses (pen, lamp) and 1 hit (second pen), got {cache.misses} misses and {cache.hits} hits. "
        "Call cache.get_or_compute for every known sku."
    )


def test_dict_cache_from_the_module_still_works():
    cache = DictCache()
    assert order_total(ORDERS, cache=cache) == 40, "DictCache must keep working."
    assert cache.data == {"pen": 2, "lamp": 30}, "DictCache keeps the unit prices."


def test_both_collaborators_together():
    logger, cache = ListLogger(), CountingCache()
    assert order_total([("book", 1)], logger, cache) == 12, "Positional logger and cache arguments keep working."
    assert [r[0] for r in logger.records] == ["info", "info"], "One 'priced' and one 'total' message."


def test_separate_calls_do_not_share_state():
    order_total(ORDERS)
    cache = CountingCache()
    order_total([("pen", 1)], cache=cache)
    assert cache.misses == 1, "A fresh cache starts empty; the defaults must not leak into it."


def test_no_none_checks_in_the_functions():
    tree = ast.parse(Path(solution.__file__).read_text())
    for name in ("price_order_lines", "order_total"):
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
        for node in ast.walk(fn):
            if isinstance(node, ast.Constant) and node.value is None:
                raise AssertionError(
                    f"{name} mentions None. With NullLogger/NullCache as defaults there is nothing to check: "
                    "call logger.info(...) and cache.get_or_compute(...) directly."
                )
            if isinstance(node, (ast.If, ast.IfExp)) and any(
                isinstance(n, ast.Name) and n.id in {"logger", "cache"} for n in ast.walk(node.test)
            ):
                raise AssertionError(
                    f"{name} branches on 'logger' or 'cache'. Remove the check: the default object already does nothing."
                )
            if isinstance(node, ast.BoolOp) and any(
                isinstance(v, ast.Name) and v.id in {"logger", "cache"} for v in node.values
            ):
                raise AssertionError(f"{name} uses 'logger or ...'/'cache or ...'. Put the null object in the default instead.")
