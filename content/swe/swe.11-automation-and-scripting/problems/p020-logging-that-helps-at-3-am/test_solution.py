import io
import logging
import re

import pytest

from solution import setup_logging

STAMP = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


@pytest.fixture(autouse=True)
def clean_logger():
    yield
    log = logging.getLogger("auto")
    for h in list(log.handlers):
        log.removeHandler(h)
        h.close()


def emit_all():
    log = logging.getLogger("auto")
    log.debug("d-msg")
    log.info("i-msg")
    log.warning("w-msg")


def test_returns_the_auto_logger():
    assert setup_logging(stream=io.StringIO()) is logging.getLogger("auto"), "Configure and return logging.getLogger('auto')."


@pytest.mark.parametrize("verbose, shown, hidden", [
    (0, ["w-msg"], ["i-msg", "d-msg"]),
    (1, ["w-msg", "i-msg"], ["d-msg"]),
    (2, ["w-msg", "i-msg", "d-msg"], []),
    (5, ["w-msg", "i-msg", "d-msg"], []),
])
def test_console_level_follows_verbose(verbose, shown, hidden):
    stream = io.StringIO()
    setup_logging(verbose=verbose, stream=stream)
    emit_all()
    text = stream.getvalue()
    for word in shown:
        assert word in text, f"verbose={verbose}: {word} must reach the console (0=WARNING, 1=INFO, 2+=DEBUG)."
    for word in hidden:
        assert word not in text, f"verbose={verbose}: {word} must NOT reach the console."


def test_console_format():
    stream = io.StringIO()
    setup_logging(stream=stream)
    logging.getLogger("auto").warning("disk at %d%%", 91)
    assert stream.getvalue() == "WARNING auto: disk at 91%\n", f"Console format '%(levelname)s %(name)s: %(message)s'; got {stream.getvalue()!r}"


def test_file_gets_everything_with_timestamps(tmp_path):
    logfile = tmp_path / "auto.log"
    stream = io.StringIO()
    setup_logging(verbose=0, logfile=logfile, stream=stream)
    emit_all()
    assert "d-msg" not in stream.getvalue(), "The console stays at WARNING with verbose=0..."
    lines = logfile.read_text(encoding="utf-8").splitlines()
    assert [line.split(" ", 2)[2] for line in lines] == ["DEBUG auto: d-msg", "INFO auto: i-msg", "WARNING auto: w-msg"], \
        f"...but the file always gets DEBUG and up. The logger itself must be at DEBUG. File: {lines}"
    assert all(STAMP.match(line) for line in lines), "Every file line starts with the date and time (%(asctime)s)."


def test_child_loggers_reach_the_handlers(tmp_path):
    stream = io.StringIO()
    setup_logging(verbose=1, stream=stream)
    logging.getLogger("auto.tidy").info("moved 3 files")
    assert "INFO auto.tidy: moved 3 files" in stream.getvalue(), "Records of 'auto.tidy' travel up to the 'auto' handlers."


def test_does_not_propagate_to_root():
    setup_logging(stream=io.StringIO())
    assert logging.getLogger("auto").propagate is False, "Set propagate = False, or a root handler prints every line again."


def test_calling_twice_does_not_duplicate(tmp_path):
    first = io.StringIO()
    setup_logging(verbose=1, logfile=tmp_path / "a.log", stream=first)
    second = io.StringIO()
    log = setup_logging(verbose=1, logfile=tmp_path / "a.log", stream=second)
    assert len(log.handlers) == 2, f"After two calls there must still be exactly 2 handlers (console + file); got {len(log.handlers)}"
    log.info("once")
    assert second.getvalue().count("once") == 1 and "once" not in first.getvalue(), "Old handlers must be removed: each message once."
    assert (tmp_path / "a.log").read_text(encoding="utf-8").count("once") == 1, "The file gets the message once too."


def test_no_file_handler_without_logfile():
    log = setup_logging(stream=io.StringIO())
    assert len(log.handlers) == 1, "Without logfile there is only the console handler."
