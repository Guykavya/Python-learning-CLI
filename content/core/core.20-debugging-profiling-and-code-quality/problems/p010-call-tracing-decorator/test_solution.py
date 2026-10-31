import logging

import pytest

from solution import trace_calls


@pytest.fixture
def log(request, caplog):
    name = "p010." + request.node.name
    caplog.set_level(logging.DEBUG, logger=name)
    return logging.getLogger(name)


def messages(caplog, log):
    return [r.getMessage() for r in caplog.records if r.name == log.name]


def test_logs_call_and_result(log, caplog):
    @trace_calls(log)
    def area(w, h, unit="m"):
        return f"{w * h} {unit}2"

    assert area(3, 4, unit="cm") == "12 cm2", "The decorated function must return what the original returns."
    assert messages(caplog, log) == ["call area(3, 4, unit='cm')", "area -> '12 cm2'"], (
        f"Got {messages(caplog, log)}. Expected 'call name(args)' then 'name -> repr(result)'."
    )


def test_all_records_are_debug(log, caplog):
    @trace_calls(log)
    def one():
        return 1

    one()
    levels = {r.levelname for r in caplog.records if r.name == log.name}
    assert levels == {"DEBUG"}, f"Tracing belongs at DEBUG level, got {levels}."


def test_argument_text(log, caplog):
    @trace_calls(log)
    def f(*args, **kwargs):
        return None

    f()
    f("a", [1, 2])
    f(x=None, y="q")
    msgs = messages(caplog, log)
    assert msgs[0] == "call f()", f"No arguments: 'call f()', got {msgs[0]!r}."
    assert msgs[2] == "call f('a', [1, 2])", f"Positional args as repr joined by ', ', got {msgs[2]!r}."
    assert msgs[4] == "call f(x=None, y='q')", (
        f"Keyword args as key=repr(value) in the order given, got {msgs[4]!r}."
    )
    assert msgs[1] == "f -> None", f"A None result is logged as 'f -> None', got {msgs[1]!r}."


def test_exception_logged_and_reraised(log, caplog):
    boom = ValueError("bad age")

    @trace_calls(log)
    def parse_age(text):
        raise boom

    try:
        parse_age("ten")
    except ValueError as exc:
        caught = exc
    else:
        pytest.fail("The exception disappeared. After logging it, re-raise it with a bare 'raise'.")
    assert caught is boom, "Re-raise the SAME exception object (a bare 'raise'), do not wrap it."
    assert messages(caplog, log) == ["call parse_age('ten')", "parse_age raised ValueError('bad age')"], (
        f"Got {messages(caplog, log)}. On an exception log 'name raised repr(exc)' and no '->' line."
    )


def test_metadata_kept(log):
    def area(w, h):
        """Area of a rectangle."""
        return w * h

    wrapped = trace_calls(log)(area)
    assert wrapped.__name__ == "area", "Use functools.wraps(func) so the wrapper keeps the name."
    assert wrapped.__doc__ == "Area of a rectangle.", "functools.wraps also copies the docstring."
    assert wrapped.__wrapped__ is area, "functools.wraps sets __wrapped__ to the original function."


def test_lazy_formatting(log, caplog):
    @trace_calls(log)
    def double(n):
        return n * 2

    double(21)
    recs = [r for r in caplog.records if r.name == log.name]
    assert recs[0].msg == "call %s(%s)" and recs[0].args == ("double", "21"), (
        "Pass the values as arguments: logger.debug('call %s(%s)', name, arg_text). "
        f"Got msg={recs[0].msg!r} args={recs[0].args!r}."
    )
    assert recs[1].msg == "%s -> %r" and recs[1].args == ("double", 42), (
        f"Use logger.debug('%s -> %r', name, result). Got msg={recs[1].msg!r} args={recs[1].args!r}."
    )


class Costly:
    reprs = 0

    def __repr__(self):
        Costly.reprs += 1
        return "Costly()"


def test_no_repr_when_debug_is_off(caplog):
    quiet = logging.getLogger("p010.quiet")
    quiet.setLevel(logging.WARNING)
    try:
        @trace_calls(quiet)
        def same(x):
            return x

        Costly.reprs = 0
        obj = Costly()
        assert same(obj) is obj, "The function must still run when DEBUG is off."
        assert Costly.reprs == 0, (
            f"repr() was called {Costly.reprs} times although DEBUG is off. Check "
            "logger.isEnabledFor(logging.DEBUG) first and just call the function."
        )
    finally:
        quiet.setLevel(logging.NOTSET)


def test_nothing_printed(log, capsys):
    @trace_calls(log)
    def one():
        return 1

    one()
    assert capsys.readouterr().out == "", "Do not print: log through the logger."
