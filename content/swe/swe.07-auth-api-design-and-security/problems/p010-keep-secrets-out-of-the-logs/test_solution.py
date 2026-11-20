import logging

import pytest

from solution import RedactSecrets


@pytest.fixture
def log(caplog):
    logger = logging.getLogger("swe07.p010")
    logger.setLevel(logging.INFO)
    f = RedactSecrets()
    logger.addFilter(f)
    caplog.set_level(logging.INFO, logger="swe07.p010")
    yield logger
    logger.removeFilter(f)


def logged(caplog):
    assert len(caplog.records) == 1, "The record must still be logged: filter() has to return True."
    return caplog.records[0].getMessage()


def test_plain_message_is_unchanged(log, caplog):
    log.info("order 17 cancelled by user 1")
    assert logged(caplog) == "order 17 cancelled by user 1", "A message with nothing sensitive must come out exactly as it went in."


def test_percent_arguments_are_still_formatted(log, caplog):
    log.info("order %s cancelled by user %d", 17, 1)
    assert logged(caplog) == "order 17 cancelled by user 1", "Ordinary %-arguments must still be filled in."


def test_password_in_text(log, caplog):
    log.warning("login failed for ada, password=hunter2 from 10.0.0.9")
    msg = logged(caplog)
    assert "hunter2" not in msg, "The password value is still in the log line: mask name=value text."
    assert msg == "login failed for ada, password=[REDACTED] from 10.0.0.9", f"Only the value changes; got {msg!r}"


def test_name_is_case_insensitive(log, caplog):
    log.info("PASSWORD=abc Token=def API_KEY=ghi")
    assert logged(caplog) == "PASSWORD=[REDACTED] Token=[REDACTED] API_KEY=[REDACTED]", "Names match in any capitalisation, and the name keeps its own spelling."


def test_value_stops_at_separator(log, caplog):
    log.info("GET /search?q=books&token=abc123&page=2")
    assert logged(caplog) == "GET /search?q=books&token=[REDACTED]&page=2", "The value ends at '&', space, comma or ';'."
    log.info("a=1;password=x;b=2, token=y, c=3")
    assert caplog.records[1].getMessage() == "a=1;password=[REDACTED];b=2, token=[REDACTED], c=3"


def test_authorization_bearer_takes_two_words(log, caplog):
    log.info("headers authorization=Bearer eyJhbGciOi.payload.sig accept=json")
    msg = logged(caplog)
    assert "eyJhbGciOi" not in msg, "A 'Bearer <token>' value has two words: mask the token after 'Bearer' too."
    assert msg == "headers authorization=[REDACTED] accept=json", f"got {msg!r}"


def test_name_inside_a_longer_word_is_not_touched(log, caplog):
    log.info("tokens=3 password_age=40 mytoken=5 ok")
    assert logged(caplog) == "tokens=3 password_age=40 mytoken=5 ok", \
        "Only the standalone names count: 'tokens', 'password_age' and 'mytoken' are other words. Use a regex with (?<!\\w) before the name and '=' right after it."


def test_dict_argument(log, caplog):
    log.info("sending %s", {"user": "asha", "Token": "abc123", "meta": {"api_key": "k-1"}})
    msg = logged(caplog)
    assert "abc123" not in msg and "k-1" not in msg, f"Secrets in dict arguments (also nested ones) must be masked; got {msg!r}"
    assert "asha" in msg, "Other values stay."
    assert msg == "sending {'user': 'asha', 'Token': '[REDACTED]', 'meta': {'api_key': '[REDACTED]'}}", f"got {msg!r}"


def test_named_style_dict_arguments(log, caplog):
    log.info("%(user)s logged in with %(password)s", {"user": "asha", "password": "hunter2"})
    assert logged(caplog) == "asha logged in with [REDACTED]", "logging passes a single dict as record.args itself: handle a dict there too."


def test_dict_inside_list_and_tuple_args(log, caplog):
    log.info("rows %s and %s", [{"password": "p1"}, {"user": "u"}], ({"token": "t1"},))
    msg = logged(caplog)
    assert "p1" not in msg and "t1" not in msg, f"Look inside lists and tuples too; got {msg!r}"


def test_callers_dictionary_is_not_changed(log, caplog):
    original = {"user": "asha", "password": "hunter2", "meta": {"token": "t"}}
    log.info("data %s", original)
    assert original == {"user": "asha", "password": "hunter2", "meta": {"token": "t"}}, \
        "The caller's dict must stay as it was: build a masked COPY, do not assign into the original."


def test_record_is_finished_text(log, caplog):
    log.info("value is %s", "50%")
    rec = caplog.records[0]
    assert rec.args in (None, ()), "Set record.args to None after formatting, so a handler does not format the message a second time."
    assert rec.getMessage() == "value is 50%", "A '%' in an argument must survive."


def test_message_with_percent_and_no_args(log, caplog):
    log.info("100% done password=abc")
    assert logged(caplog) == "100% done password=[REDACTED]", "A message with a '%' and no arguments must not crash."


def test_text_of_a_non_string_message(log, caplog):
    log.info(12345)
    assert logged(caplog) == "12345", "record.msg can be any object: use record.getMessage()."
