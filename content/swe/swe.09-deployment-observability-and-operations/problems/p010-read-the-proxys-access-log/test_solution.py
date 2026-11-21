import json

import pytest

from solution import parse_access_line, summarise


def make(rid, status=200, duration=0.01, uri="/", upstream_status="200", method="GET"):
    return json.dumps({"ts": "2026-11-09T07:13:20+00:00", "remote": "172.19.0.1", "method": method, "uri": uri, "status": status,
                       "bytes": 10, "duration": duration, "upstream": "172.19.0.3:8000", "upstream_status": upstream_status,
                       "request_id": rid})


def test_parse_the_chapter_line():
    line = ('{"ts":"2026-11-09T07:13:20+00:00","remote":"172.19.0.1","method":"GET","uri":"/orders/1","status":404,"bytes":28,'
            '"duration":0.003,"upstream":"172.19.0.3:8000","upstream_status":"404","request_id":"2bd7f8f0a1ca53e9fbc29657746c07fa"}')
    assert parse_access_line(line) == {
        "request_id": "2bd7f8f0a1ca53e9fbc29657746c07fa", "method": "GET", "uri": "/orders/1", "status": 404,
        "duration": 0.003, "upstream_status": "404", "upstream_tries": 1}, \
        "Return exactly the seven keys of problem.md; status is an int, duration a float, upstream_tries counts the comma-separated parts."


def test_three_tries():
    got = parse_access_line(make("a" * 8, 504, 15.011, "/slow", "504, 504, 504"))
    assert got["upstream_tries"] == 3 and got["upstream_status"] == "504, 504, 504", "'504, 504, 504' means Nginx tried three backends."


@pytest.mark.parametrize("upstream_status", ["-", "", None])
def test_no_upstream_answered(upstream_status):
    data = {"request_id": "abc12345", "method": "GET", "uri": "/", "status": 502, "duration": 0.001}
    if upstream_status is not None:
        data["upstream_status"] = upstream_status
    got = parse_access_line(json.dumps(data))
    assert got["upstream_tries"] == 0 and got["upstream_status"] == "-", \
        "502 with upstream_status '-' (or missing): the backend never answered, 0 tries. A missing field is reported as '-'."


def test_types_are_converted():
    got = parse_access_line('{"request_id":"abc12345","method":"POST","uri":"/orders","status":"201","duration":"0.5"}')
    assert got["status"] == 201 and isinstance(got["status"], int) and got["duration"] == 0.5 and isinstance(got["duration"], float), \
        "status must be an int and duration a float, even when the log has them as text."


@pytest.mark.parametrize("line", [
    "not json at all", "", "[1, 2]", "42", '{"method":"GET"}',
    '{"request_id":"x","method":"GET","uri":"/","status":200}',
])
def test_bad_lines_raise(line):
    with pytest.raises(ValueError):
        parse_access_line(line)


def test_summarise_counts_and_share():
    lines = [make("r1", 200), make("r2", 200), make("r3", 404), make("r4", 500), make("r5", 502, upstream_status="-"),
             make("r6", 200), make("r7", 504, 5.0, upstream_status="504"), make("r8", 200), make("r9", 301), make("r10", 200)]
    got = summarise(lines)
    assert got["requests"] == 10 and got["skipped"] == 0
    assert got["by_status"] == {200: 5, 404: 1, 500: 1, 502: 1, 504: 1, 301: 1}, f"Count requests per status; got {got['by_status']}"
    assert got["share_5xx"] == pytest.approx(0.3), "3 of 10 requests (500, 502, 504) are 5xx; 404 and 301 are not."


def test_slowest_three():
    lines = [make("a", duration=0.5, uri="/a"), make("b", duration=2.0, uri="/b"), make("c", duration=1.0, uri="/c"),
             make("d", duration=2.0, uri="/d"), make("e", duration=0.1, uri="/e")]
    assert summarise(lines)["slowest"] == [
        {"request_id": "b", "uri": "/b", "duration": 2.0},
        {"request_id": "d", "uri": "/d", "duration": 2.0},
        {"request_id": "c", "uri": "/c", "duration": 1.0},
    ], "The 3 slowest, slowest first; equal durations: smaller request_id first. Each item has request_id, uri and duration."


def test_fewer_than_three_requests():
    got = summarise([make("only", duration=1.0)])
    assert len(got["slowest"]) == 1 and got["requests"] == 1


def test_noise_is_skipped_and_counted():
    lines = [make("r1"), "", "   ", "nginx: [warn] something", '{"msg": "not an access line"}', make("r2", 500)]
    got = summarise(lines)
    assert got["requests"] == 2, f"Two valid lines; got {got['requests']}"
    assert got["skipped"] == 2, f"The warning and the JSON without access fields are skipped and counted (blank lines are not): got {got['skipped']}"
    assert got["share_5xx"] == pytest.approx(0.5)


def test_empty_log():
    assert summarise([]) == {"requests": 0, "skipped": 0, "by_status": {}, "slowest": [], "share_5xx": 0.0}, \
        "An empty log gives zeros, not a ZeroDivisionError."
