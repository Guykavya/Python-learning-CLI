import logging

import pytest

from solution import safe_divide_all


@pytest.fixture
def log(request, caplog):
    """A fresh logger captured by caplog at DEBUG level."""
    name = "p008." + request.node.name
    caplog.set_level(logging.DEBUG, logger=name)
    return logging.getLogger(name)


def mine(caplog, log):
    return [r for r in caplog.records if r.name == log.name]


def test_results(log):
    assert safe_divide_all([(6, 3), (1, 0), ("7", 2), (5, 2)], log) == [2.0, None, None, 2.5], (
        "Good pairs give the quotient, bad pairs give None, and the job does not stop at the first bad pair."
    )
    assert safe_divide_all([], log) == [], "No pairs, no results."


def test_success_logged_at_debug(log, caplog):
    safe_divide_all([(6, 3)], log)
    recs = mine(caplog, log)
    assert len(recs) == 1, f"One pair should give exactly one log record, got {len(recs)}."
    assert recs[0].levelno == logging.DEBUG, "A successful division is logged at DEBUG."
    assert recs[0].getMessage() == "pair 0: 6 / 3 = 2.0", f"Got {recs[0].getMessage()!r}."


def test_zero_is_a_warning_without_traceback(log, caplog):
    safe_divide_all([(1, 1), (4, 0)], log)
    rec = mine(caplog, log)[1]
    assert rec.levelno == logging.WARNING, (
        f"Division by zero is an expected data problem: WARNING, not {rec.levelname}."
    )
    assert rec.getMessage() == "pair 1: division by zero (4 / 0)", (
        f"Got {rec.getMessage()!r}. Count pairs from 0 and use the exact template."
    )
    assert not rec.exc_info, "A warning about bad data should not carry a traceback (no exc_info)."


def test_type_error_logged_with_traceback(log, caplog):
    safe_divide_all([("7", 2)], log)
    rec = mine(caplog, log)[0]
    assert rec.levelno == logging.ERROR, f"Use logger.exception (level ERROR), got {rec.levelname}."
    assert rec.getMessage() == "pair 0: cannot divide '7' by 2", (
        f"Got {rec.getMessage()!r}. Use %r so the string shows its quotes: '7' is not 7."
    )
    assert rec.exc_info and rec.exc_info[0] is TypeError, (
        "The record has no traceback. logger.exception(...) inside the except block attaches "
        "exc_info automatically; logger.error(...) does not."
    )


def test_lazy_formatting(log, caplog):
    safe_divide_all([(6, 3), (1, 0), (None, 1)], log)
    recs = mine(caplog, log)
    assert [r.msg for r in recs] == [
        "pair %d: %r / %r = %r",
        "pair %d: division by zero (%r / %r)",
        "pair %d: cannot divide %r by %r",
    ], (
        "record.msg should be the TEMPLATE with % placeholders. You built the text yourself "
        "(f-string or %); pass the values as arguments: logger.debug(TEMPLATE, i, a, b, q)."
    )
    assert recs[0].args == (0, 6, 3, 2.0), f"record.args should be (i, a, b, q), got {recs[0].args!r}."
    assert recs[1].args == (1, 1, 0), f"record.args should be (i, a, b), got {recs[1].args!r}."


def test_other_exceptions_propagate(log):
    class Weird:
        def __truediv__(self, other):
            raise KeyError("not mine")

    try:
        safe_divide_all([(Weird(), 1)], log)
    except KeyError:
        pass
    else:
        pytest.fail(
            "A KeyError from inside the division was swallowed. Catch only ZeroDivisionError and "
            "TypeError; any other exception is a real bug and must propagate."
        )


def test_nothing_printed(log, capsys):
    safe_divide_all([(1, 0), ("x", 1)], log)
    out = capsys.readouterr().out
    assert out == "", f"Do not print: everything goes through the logger. Printed: {out!r}"
