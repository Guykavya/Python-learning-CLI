import datetime
import io
import json
import logging
import pathlib
import sys

import pytest

from solution import JsonFormatter, configure_logging, request_id_var


@pytest.fixture
def root_logging():
    root = logging.getLogger()
    saved, level = root.handlers[:], root.level
    yield root
    root.handlers[:] = saved
    root.setLevel(level)


@pytest.fixture(autouse=True)
def fresh_request_id():
    token = request_id_var.set("-")
    yield
    request_id_var.reset(token)


def record(msg="hello", args=(), level="INFO", created=1700000000.123, msecs=123.0, **extra):
    return logging.makeLogRecord({"name": "pagebound", "levelname": level, "levelno": getattr(logging, level), "msg": msg,
                                  "args": args, "created": created, "msecs": msecs, **extra})


def line_of(rec):
    return JsonFormatter().format(rec)


def test_fixed_keys_and_order():
    request_id_var.set("demo-req-0001")
    line = line_of(record("hello %s", ("world",)))
    assert line == ('{"ts":"2023-11-14T22:13:20.123Z","level":"INFO","logger":"pagebound","msg":"hello world",'
                    '"request_id":"demo-req-0001"}'), \
        f"Compact JSON, keys ts, level, logger, msg, request_id in this order, UTC time with milliseconds and a Z; got {line}"


def test_default_request_id_is_a_dash():
    assert json.loads(line_of(record()))["request_id"] == "-", "Outside a request the id is '-' (the context variable's default)."


def test_milliseconds_are_zero_padded():
    assert json.loads(line_of(record(created=1700000000.007, msecs=7.0)))["ts"] == "2023-11-14T22:13:20.007Z", \
        "Milliseconds use three digits: .007, not .7"


def test_extra_fields_are_added_after_the_fixed_keys():
    line = line_of(record("order created", fields={"order_id": 7, "item": "pen"}))
    assert list(json.loads(line)) == ["ts", "level", "logger", "msg", "request_id", "order_id", "item"], \
        "Extra fields come after the five fixed keys, in the order the caller gave them."


def test_fixed_keys_cannot_be_forged():
    request_id_var.set("real-id-0001")
    data = json.loads(line_of(record("x", fields={"level": "DEBUG", "request_id": "forged-id", "msg": "innocent", "ok": 1})))
    assert data["level"] == "INFO" and data["request_id"] == "real-id-0001" and data["msg"] == "x", \
        "A field named like a fixed key must be ignored: otherwise a caller (or an attacker's input) can forge the level or the request id."
    assert data["ok"] == 1


def test_exception_is_one_string_on_one_line():
    try:
        raise RuntimeError("simulated bug while building the invoice")
    except RuntimeError:
        rec = record("unhandled error", level="ERROR", exc_info=sys.exc_info())
    line = line_of(rec)
    assert "\n" not in line, "A record must be ONE line: json.dumps escapes the newlines of the traceback."
    data = json.loads(line)
    assert data["exception"].startswith("Traceback (most recent call last):"), "The traceback goes into an 'exception' string."
    assert data["exception"].rstrip().endswith("RuntimeError: simulated bug while building the invoice")
    assert list(data)[-1] == "exception", "The exception key is added last."


def test_messages_with_newlines_stay_on_one_line():
    line = line_of(record("two\nlines\r\nhere"))
    assert "\n" not in line and "\r" not in line, "Line breaks inside a message must be escaped, or a user could forge a second log line."
    assert json.loads(line)["msg"] == "two\nlines\r\nhere"


def test_values_json_cannot_write():
    line = line_of(record("x", fields={"path": pathlib.PurePosixPath("/srv/app"), "when": datetime.date(2026, 11, 9), "n": None, "ok": True}))
    data = json.loads(line)
    assert data["path"] == "/srv/app" and data["when"] == "2026-11-09", "Write values that JSON does not know with str() (default=str)."
    assert data["n"] is None and data["ok"] is True, "Normal JSON values stay normal."


def test_unicode_survives():
    assert json.loads(line_of(record("café ☕ 日本語")))["msg"] == "café ☕ 日本語"


def test_configure_logging_installs_one_json_handler(root_logging):
    stream = io.StringIO()
    root_logging.addHandler(logging.StreamHandler())          # an old handler that must be replaced
    configure_logging("WARNING", stream)
    assert len(root_logging.handlers) == 1, "configure_logging replaces the root handlers by exactly one."
    assert root_logging.level == logging.WARNING, "The root level is the one given."
    request_id_var.set("abc-request-1")
    log = logging.getLogger("pagebound")
    log.info("too quiet")
    log.warning("careful", extra={"fields": {"disk": "93%"}})
    lines = stream.getvalue().splitlines()
    assert len(lines) == 1, f"INFO is below WARNING: expected one line, got {lines}"
    data = json.loads(lines[0])
    assert (data["level"], data["msg"], data["request_id"], data["disk"]) == ("WARNING", "careful", "abc-request-1", "93%")


def test_configure_logging_defaults_to_stdout(root_logging, capsys):
    configure_logging("INFO")
    logging.getLogger("pagebound").info("to stdout")
    out = capsys.readouterr().out.strip()
    assert json.loads(out)["msg"] == "to stdout", "With no stream the logs go to sys.stdout (the platform collects stdout)."
