import logging

import pytest

from solution import level_for, make_logger, process_orders

ORDERS = [("A1", 5), ("A2", 0), ("A3", 250)]


@pytest.fixture
def name(request):
    """A unique logger name per test, reset afterwards so tests do not affect each other."""
    logger_name = f"p056.{request.node.name}"
    yield logger_name
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.NOTSET)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)


def lines(caplog, logger_name):
    return [(r.levelname, r.getMessage()) for r in caplog.records if r.name == logger_name]


def test_level_for():
    assert level_for(0) == logging.WARNING, "Verbosity 0 (the default) shows WARNING and above."
    assert level_for(1) == logging.INFO, "-v gives INFO."
    assert level_for(2) == logging.DEBUG, "-vv gives DEBUG."
    assert level_for(5) == logging.DEBUG, "More v's than 2 still give DEBUG (there is nothing below)."
    assert level_for(-1) == logging.ERROR, "A negative verbosity (--quiet) shows only ERROR and above."


def test_make_logger(name):
    logger = make_logger(name, 1)
    assert isinstance(logger, logging.Logger) and logger.name == name, "Use logging.getLogger(name)."
    assert logger.level == logging.INFO, "Set the logger's level with logger.setLevel(level_for(verbosity))."
    assert logger.isEnabledFor(logging.INFO) and not logger.isEnabledFor(logging.DEBUG), "At INFO, DEBUG messages are dropped."
    assert logger.handlers == [], "Do not add handlers in make_logger: where logs go is decided by the application."
    assert make_logger(name, 0) is logger and logger.level == logging.WARNING, (
        "getLogger returns the SAME logger for the same name; calling make_logger again just changes its level."
    )


def test_process_orders_debug(name, caplog):
    caplog.set_level(logging.DEBUG, logger=name)
    assert process_orders(ORDERS, logging.getLogger(name)) == 2, "A1 and A3 are valid (A3 is large but valid); A2 is not."
    assert lines(caplog, name) == [
        ("DEBUG", "checking order A1"),
        ("DEBUG", "checking order A2"),
        ("ERROR", "invalid quantity 0 in order A2"),
        ("DEBUG", "checking order A3"),
        ("WARNING", "large order A3: 250 items"),
        ("INFO", "processed 3 orders, 1 invalid"),
    ], "Check the level and exact text of each message, and their order (debug first for every order, summary last)."


def test_levels_filter(name, caplog):
    logger = make_logger(name, 0)
    process_orders(ORDERS, logger)
    assert lines(caplog, name) == [
        ("ERROR", "invalid quantity 0 in order A2"),
        ("WARNING", "large order A3: 250 items"),
    ], "At WARNING (verbosity 0) the DEBUG and INFO messages must be dropped: use logger.debug/info, not warning, for them."


def test_quiet(name, caplog):
    logger = make_logger(name, -1)
    process_orders(ORDERS, logger)
    assert lines(caplog, name) == [("ERROR", "invalid quantity 0 in order A2")], "--quiet (ERROR) keeps only the error."


def test_lazy_formatting(name, caplog):
    caplog.set_level(logging.DEBUG, logger=name)
    process_orders([("B7", -3), ("B8", 101)], logging.getLogger(name))
    records = [r for r in caplog.records if r.name == name]
    assert records, "process_orders must log through the logger it receives."
    for r in records:
        assert r.args, (
            f"The message {r.getMessage()!r} was formatted before logging. Pass the values as arguments: "
            "logger.warning('large order %s: %d items', order_id, quantity)."
        )
    assert {r.msg for r in records} == {
        "checking order %s",
        "invalid quantity %d in order %s",
        "large order %s: %d items",
        "processed %d orders, %d invalid",
    }, "Use exactly the four message templates from the problem."


def test_edge_cases(name, caplog):
    caplog.set_level(logging.DEBUG, logger=name)
    assert process_orders([], logging.getLogger(name)) == 0, "No orders: 0 valid."
    assert lines(caplog, name) == [("INFO", "processed 0 orders, 0 invalid")], "The summary is logged even for an empty list."
    caplog.clear()
    assert process_orders([("C1", 100), ("C2", 1)], logging.getLogger(name)) == 2, "100 is not MORE than 100: no warning, valid."
    assert [lvl for lvl, _ in lines(caplog, name)] == ["DEBUG", "DEBUG", "INFO"], "Exactly 100 items is not a large order."
