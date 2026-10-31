import io
import logging

import pytest

from solution import make_logger


@pytest.fixture
def name(request):
    """A logger name used by no other test; cleaned up afterwards."""
    logger_name = "p007." + request.node.name
    yield logger_name
    logger = logging.getLogger(logger_name)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    logger.setLevel(logging.NOTSET)
    logger.propagate = True


def test_returns_the_named_logger(name):
    log = make_logger(name, logging.INFO, io.StringIO())
    assert log is logging.getLogger(name), "Use logging.getLogger(name) so the same name gives the same logger."
    assert log.level == logging.INFO, f"Set the logger's level to the given level, got {log.level}."


def test_format_and_level_filtering(name):
    buf = io.StringIO()
    log = make_logger(name, logging.INFO, buf)
    log.debug("hidden")
    log.info("added %s x%d", "pen", 3)
    assert buf.getvalue() == f"INFO {name}: added pen x3\n", (
        f"Got {buf.getvalue()!r}. Use the formatter '%(levelname)s %(name)s: %(message)s' and "
        "set the level so DEBUG is dropped."
    )


def test_writes_to_the_given_stream(name):
    buf = io.StringIO()
    make_logger(name, logging.WARNING, buf).error("boom")
    assert buf.getvalue() == f"ERROR {name}: boom\n", (
        "Write to the stream argument: logging.StreamHandler(stream). Without it, the handler "
        "writes to sys.stderr."
    )


def test_repeat_calls_do_not_duplicate_lines(name):
    buf = io.StringIO()
    make_logger(name, logging.INFO, buf)
    make_logger(name, logging.INFO, buf)
    log = make_logger(name, logging.INFO, buf)
    log.warning("stock low")
    assert buf.getvalue() == f"WARNING {name}: stock low\n", (
        f"Got {buf.getvalue()!r}. Each call added another handler, so the line is printed once per "
        "call. Remove the old handlers before adding the new one."
    )
    assert len(log.handlers) == 1, f"The logger should have exactly 1 handler, has {len(log.handlers)}."


def test_second_call_switches_stream_and_level(name):
    first, second = io.StringIO(), io.StringIO()
    make_logger(name, logging.ERROR, first)
    log = make_logger(name, logging.DEBUG, second)
    log.debug("now visible")
    assert first.getvalue() == "", "After the second call the OLD stream must get nothing."
    assert second.getvalue() == f"DEBUG {name}: now visible\n", (
        "The second call must use the NEW stream and the NEW level."
    )


def test_does_not_propagate(name, caplog):
    caplog.set_level(logging.DEBUG)
    log = make_logger(name, logging.INFO, io.StringIO())
    log.info("only once")
    assert log.propagate is False, "Set logger.propagate = False."
    assert not [r for r in caplog.records if r.name == name], (
        "The record reached the root logger. With propagate left True, an app that also "
        "configures the root logger prints every line twice."
    )
