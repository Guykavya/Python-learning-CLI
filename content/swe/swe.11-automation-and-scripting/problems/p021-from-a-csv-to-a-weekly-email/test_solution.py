from email.message import EmailMessage

from solution import FakeTransport, build_email, send, summarize

EXPORT = "region,amount\nnorth,1200.50\nsouth,830\nnorth,99.50\neast,abc\nwest,410.25\n,12\n"


def test_totals_and_bad_lines():
    totals, bad = summarize(EXPORT)
    assert totals == {"north": 1300.0, "south": 830.0, "west": 410.25}, f"Sum per region; got {totals}"
    assert bad == [5, 7], f"Line 5 (amount 'abc') and line 7 (no region) are bad; the header is line 1. Got {bad}"


def test_regions_are_sorted_and_stripped():
    totals, _ = summarize("region,amount\n west ,1\neast,2\n")
    assert list(totals) == ["east", "west"], "Strip spaces from the region and sort the totals by region."


def test_bad_row_leaves_no_trace():
    totals, bad = summarize("region,amount\nnorth,10\neast,abc\n")
    assert totals == {"north": 10.0}, "A bad row must not create an 'east' entry: convert the amount before adding."
    assert bad == [3]


def test_short_row_is_bad_not_a_crash():
    totals, bad = summarize("region,amount\nnorth,5\neast\n")
    assert bad == [3] and totals == {"north": 5.0}, "A row with a missing column gives None; float(None) raises TypeError: catch it."


def test_empty_export():
    assert summarize("region,amount\n") == ({}, []), "Only a header: no totals, no bad lines."


def test_email_headers_and_body():
    totals, bad = summarize(EXPORT)
    msg = build_email(totals, bad, "reports@example.com", "boss@example.com")
    assert isinstance(msg, EmailMessage)
    assert msg["Subject"] == "Weekly sales: 2,540.25", f"Subject uses the grand total with :,.2f; got {msg['Subject']!r}"
    assert msg["From"] == "reports@example.com" and msg["To"] == "boss@example.com"
    body = msg.get_content().splitlines()
    assert body[:4] == ["north        1,300.00", "south          830.00", "west           410.25", "TOTAL        2,540.25"], \
        f"One line per region with f'{{region:10}} {{amount:10,.2f}}', then TOTAL. Got {body[:4]}"
    assert body[4] == "" and body[5] == "Warning: could not read line(s) [5, 7]. Please check the export.", \
        "Report the bad lines in the e-mail, after an empty line: never hide them."


def test_no_warning_when_all_rows_are_good():
    msg = build_email({"north": 10.0}, [], "a@example.com", "b@example.com")
    assert "Warning" not in msg.get_content(), "Only add the warning when there are bad lines."
    assert msg["Subject"] == "Weekly sales: 10.00"


def test_send_uses_the_transport():
    transport = FakeTransport()
    msg = build_email({"north": 10.0}, [], "a@example.com", "b@example.com")
    send(msg, transport)
    assert transport.sent == [msg], "send() hands the message to transport.send_message, exactly once."


def test_end_to_end_with_a_fake():
    transport = FakeTransport()
    totals, bad = summarize(EXPORT)
    send(build_email(totals, bad, "reports@example.com", "boss@example.com"), transport)
    sent = transport.sent[0]
    assert sent["To"] == "boss@example.com" and "TOTAL" in sent.get_content()
