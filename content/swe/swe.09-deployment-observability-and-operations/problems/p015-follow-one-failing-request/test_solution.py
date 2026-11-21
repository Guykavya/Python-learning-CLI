import json

from solution import trace_request

RID = "8fad38b4c1e2"


def line(ts, service, level, msg, request_id=RID, **extra):
    return json.dumps({"ts": ts, "service": service, "level": level, "logger": "pagebound", "msg": msg, "request_id": request_id, **extra})


LOG = [
    line("2026-11-09T07:00:00.100Z", "web", "INFO", "request finished", "someone-else-1"),
    "docker: restarting the log driver",
    line("2026-11-09T07:00:03.000Z", "worker", "ERROR", "report failed", exception="Traceback ..."),
    line("2026-11-09T07:00:01.000Z", "web", "INFO", "report requested"),
    "",
    line("2026-11-09T07:00:02.000Z", "worker", "INFO", "report started"),
    '{"truncated": ',
    line("2026-11-09T07:00:04.000Z", "web", "ERROR", "unhandled error"),
    line("2026-11-09T07:00:05.000Z", "web", "INFO", "request finished", status=500),
    "[1, 2, 3]",
    line("2026-11-09T07:00:02.500Z", "worker", "INFO", "report finished", "another-request"),
]


def test_the_whole_story_in_time_order():
    result = trace_request(LOG, RID)
    assert [(e["ts"][11:19], e["service"], e["msg"]) for e in result["events"]] == [
        ("07:00:01", "web", "report requested"),
        ("07:00:02", "worker", "report started"),
        ("07:00:03", "worker", "report failed"),
        ("07:00:04", "web", "unhandled error"),
        ("07:00:05", "web", "request finished"),
    ], "Only this request's lines, sorted by ts (the lines were not in time order in the log)."


def test_events_have_exactly_four_keys():
    for event in trace_request(LOG, RID)["events"]:
        assert set(event) == {"ts", "service", "level", "msg"}, f"Each event has exactly ts, service, level and msg; got {sorted(event)}"


def test_first_error_is_the_earliest_by_time_not_by_position():
    first = trace_request(LOG, RID)["first_error"]
    assert (first["service"], first["msg"]) == ("worker", "report failed"), \
        f"The first ERROR in TIME order is the worker's failure at 07:00:03 (it comes before the web error); got {first}"


def test_services_in_order_of_first_event():
    assert trace_request(LOG, RID)["services"] == ["web", "worker"], "The request started in web, then reached the worker."


def test_no_error():
    lines = [line("2026-11-09T07:00:01.000Z", "web", "INFO", "ok"), line("2026-11-09T07:00:02.000Z", "web", "WARNING", "slow")]
    assert trace_request(lines, RID)["first_error"] is None, "WARNING is not an error; first_error is None when there is none."


def test_critical_counts_as_error():
    lines = [line("2026-11-09T07:00:01.000Z", "web", "CRITICAL", "disk full")]
    assert trace_request(lines, RID)["first_error"]["msg"] == "disk full"


def test_unknown_request_id():
    assert trace_request(LOG, "nothing-like-this") == {"events": [], "first_error": None, "services": []}, \
        "A request id that is nowhere in the logs gives an empty result (the request never reached you: check the edge)."


def test_request_id_must_match_exactly():
    lines = [line("2026-11-09T07:00:01.000Z", "web", "INFO", "x", "ABC12345"), line("2026-11-09T07:00:02.000Z", "web", "INFO", "y", "abc12345-extra")]
    assert trace_request(lines, "abc12345") == {"events": [], "first_error": None, "services": []}, \
        "Compare ids exactly: no case folding, no prefix match."


def test_missing_fields_get_defaults():
    lines = [json.dumps({"request_id": RID}), json.dumps({"request_id": RID, "ts": "2026-11-09T07:00:00Z", "service": "web", "level": "INFO", "msg": "late"})]
    result = trace_request(lines, RID)
    assert result["events"][0] == {"ts": "", "service": "unknown", "level": "", "msg": ""}, \
        "Missing fields: service becomes 'unknown', the others ''. A missing ts sorts first."
    assert result["services"] == ["unknown", "web"]


def test_same_timestamp_keeps_input_order():
    lines = [line("2026-11-09T07:00:01.000Z", "web", "INFO", "first"), line("2026-11-09T07:00:01.000Z", "worker", "INFO", "second")]
    assert [e["msg"] for e in trace_request(lines, RID)["events"]] == ["first", "second"], "list.sort is stable: equal timestamps keep their input order."


def test_non_string_lines_do_not_crash():
    assert trace_request([None, 42, line("2026-11-09T07:00:01.000Z", "web", "INFO", "ok")], RID)["services"] == ["web"], \
        "Anything that cannot be parsed as a JSON object is skipped (json.loads raises TypeError for None)."
