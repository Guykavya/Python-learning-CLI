import io
import logging
from datetime import datetime

import pytest

from solution import RequestIdFilter, close_logging, setup_logging


@pytest.fixture
def name(request):
    logger_name = f"p057.{request.node.name}"
    yield logger_name
    for n in (logger_name, logger_name + ".db"):
        logger = logging.getLogger(n)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True


def file_lines(path):
    return path.read_text(encoding="utf-8").splitlines()


def split_line(line):
    """'2025-03-01 10:15:02 DEBUG    [-] name: msg' -> (datetime, rest)."""
    stamp, rest = line[:19], line[20:]
    return datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S"), rest


def test_filter_adds_request_id():
    record = logging.LogRecord("x", logging.INFO, __file__, 1, "hello", None, None)
    assert RequestIdFilter("req-7").filter(record) is True, "filter() must return True so the record is kept."
    assert record.request_id == "req-7", "filter() must set record.request_id."
    assert RequestIdFilter().request_id == "-", "The default request id is '-'."


def test_console_shows_warnings_only(name, tmp_path):
    console = io.StringIO()
    log = setup_logging(name, tmp_path / "app.log", console)
    log.debug("cart has %d items", 3)
    log.info("user logged in")
    log.warning("disk almost full")
    log.error("payment failed")
    close_logging(log)
    assert console.getvalue() == "WARNING: disk almost full\nERROR: payment failed\n", (
        "The console handler has level WARNING and the format '%(levelname)s: %(message)s'. Set the level on the HANDLER; "
        "the logger itself stays at DEBUG so the file gets everything."
    )


def test_file_gets_everything_with_format(name, tmp_path):
    path = tmp_path / "app.log"
    log = setup_logging(name, path, io.StringIO(), request_id="req-42")
    log.debug("cart has %d items", 3)
    log.warning("disk almost full")
    close_logging(log)
    lines = file_lines(path)
    assert len(lines) == 2, "The file handler (level DEBUG) must record the debug message too."
    rests = []
    for line in lines:
        try:
            _, rest = split_line(line)
        except ValueError:
            pytest.fail(f"Each file line must start with the time as 'YYYY-MM-DD HH:MM:SS' (datefmt): got {line!r}")
        rests.append(rest)
    assert rests == [
        f"DEBUG    [req-42] {name}: cart has 3 items",
        f"WARNING  [req-42] {name}: disk almost full",
    ], "File format: '%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s'; -8 pads the level to 8 characters."


def test_console_level_parameter(name, tmp_path):
    console = io.StringIO()
    log = setup_logging(name, tmp_path / "a.log", console, console_level=logging.INFO)
    log.debug("hidden")
    log.info("shown")
    close_logging(log)
    assert console.getvalue() == "INFO: shown\n", "console_level sets the console handler's level."


def test_calling_setup_twice_does_not_duplicate(name, tmp_path):
    console = io.StringIO()
    path = tmp_path / "app.log"
    setup_logging(name, path, console)
    log = setup_logging(name, path, console)
    assert len(log.handlers) == 2, "After two setups the logger must still have exactly 2 handlers: remove old ones first."
    log.error("once")
    close_logging(log)
    assert console.getvalue() == "ERROR: once\n", "Each message must appear once, not once per setup call."
    assert sum("once" in line for line in file_lines(path)) == 1, "The file must get the message once too."


def test_does_not_propagate_to_root(name, tmp_path, caplog):
    log = setup_logging(name, tmp_path / "a.log", io.StringIO())
    log.error("only here")
    close_logging(log)
    assert log.propagate is False, "Set logger.propagate = False."
    assert not [r for r in caplog.records if r.name == name], (
        "The record reached the root logger's handlers: with propagate=False it is handled only by this logger's handlers."
    )


def test_child_logger_gets_request_id(name, tmp_path):
    console = io.StringIO()
    path = tmp_path / "app.log"
    log = setup_logging(name, path, console, request_id="req-9")
    logging.getLogger(name + ".db").error("connection lost")
    close_logging(log)
    lines = file_lines(path)
    assert len(lines) == 1, (
        "A child logger's record propagates to the parent's handlers and must be written once. If it is missing, the "
        "formatter failed on %(request_id)s: the filter must be on the file HANDLER, not on the logger."
    )
    assert split_line(lines[0])[1] == f"ERROR    [req-9] {name}.db: connection lost", (
        "The child's record needs request_id too: add the filter to the HANDLER (logger filters skip propagated records). "
        "%(name)s is the child's name."
    )
    assert console.getvalue() == "ERROR: connection lost\n", "The console shows the child's error as well."


def test_unicode_in_file(name, tmp_path):
    path = tmp_path / "u.log"
    log = setup_logging(name, path, io.StringIO())
    log.info("café ✓ नमस्ते")
    close_logging(log)
    assert file_lines(path)[0].endswith("café ✓ नमस्ते"), "Open the log file with encoding='utf-8' (FileHandler(..., encoding='utf-8'))."


def test_close_logging(name, tmp_path):
    path = tmp_path / "c.log"
    log = setup_logging(name, path, io.StringIO())
    handlers = list(log.handlers)
    close_logging(log)
    assert log.handlers == [], "close_logging must remove every handler from the logger."
    file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
    assert file_handlers and file_handlers[0].stream is None, "close_logging must CLOSE the handlers (FileHandler.close releases the file)."
    path.unlink()          # works on Windows only when the file is closed
    assert not path.exists(), "The closed log file can be deleted."
