import copy

from solution import lint_definition

GOOD = {
    "name": "jobs_completed", "question": "how much work was finished?", "grain": "job",
    "numerator": "jobs with status = 'completed'", "denominator": "-", "date_basis": "completed_at (IST)",
    "time_zone": "IST", "period": ">= 2025-02-01 and < 2025-03-01", "exclusions": "none",
    "owner": "finance", "version": "v2",
}


def spec(**changes):
    out = dict(GOOD)
    out.update(changes)
    return out


def test_a_clean_definition_has_no_problems():
    assert lint_definition(GOOD) == [], "a complete, precise definition must give an empty list, got %s" % lint_definition(GOOD)


def test_missing_field_empty_none_or_absent():
    s = spec(owner="", question="   ", grain=None)
    del s["version"]
    assert lint_definition(s) == ["missing: question", "missing: grain", "missing: owner", "missing: version"], (
        "list one 'missing: <field>' per field that is absent, None or blank, in the order of the REQUIRED list "
        "(name, question, grain, numerator, ...). Got %s" % lint_definition(s))


def test_dash_denominator_is_an_answer():
    assert lint_definition(spec(denominator="-")) == [], "'-' means 'not a rate' and is a valid denominator."


def test_empty_spec_lists_every_field_and_the_time_zone():
    got = lint_definition({})
    want = ["missing: " + f for f in ["name", "question", "grain", "numerator", "denominator", "date_basis", "period",
                                       "exclusions", "owner", "version"]] + ["no time zone: say UTC or IST"]
    assert got == want, "an empty spec has ten missing fields and no time zone, in that order. Got %s" % got


def test_vague_word_without_a_rule():
    got = lint_definition(spec(numerator="Active customers", exclusions="invalid or recent tests"))
    assert got == ["vague: numerator uses 'active' without a rule",
                   "vague: exclusions uses 'recent' without a rule",
                   "vague: exclusions uses 'valid' without a rule"], (
        "look for the words in lower case (any capitals), fields in the order numerator, denominator, exclusions, "
        "words in the order active, recent, valid. NOTE: 'invalid' contains 'valid', so it is reported too. Got %s" % got)


def test_vague_word_with_a_rule_is_fine():
    for text in ["active = a job created in the last 90 days", "recent: created_at > 2025-03-01", "valid when amount > 0"]:
        assert lint_definition(spec(numerator=text)) == [], "a text with a digit or one of = < > has a rule: %r" % text


def test_closed_interval():
    msg = ["closed interval: write the period as start <= t < end"]
    for period in ["created_at between '2025-02-01' and '2025-02-28'", "BETWEEN 1 AND 5",
                   ">= 2025-02-01 and <= 2025-02-28", "t <= '2025-02-28'", "t <=2025-02-28"]:
        assert lint_definition(spec(period=period)) == msg, "this period is closed on the right and must be reported: %r" % period


def test_half_open_period_is_not_reported():
    for period in [">= 2025-02-01 and < 2025-03-01", "start <= t < end"]:
        assert lint_definition(spec(period=period)) == [], (
            "a half-open period is correct: %r. Only '<=' followed by a date or number is a closed end." % period)


def test_time_zone_rules():
    no_tz = "no time zone: say UTC or IST"
    assert lint_definition(spec(time_zone="", date_basis="completed_at")) == [no_tz], "no time_zone and none in date_basis: report it."
    assert lint_definition(spec(time_zone="", date_basis="completed_at (UTC)")) == [], "'UTC' in the date basis counts as a time zone."
    assert lint_definition(spec(time_zone=None, date_basis="created_at IST")) == [], "'IST' in the date basis counts as a time zone."
    s = spec()
    del s["time_zone"]
    assert lint_definition(s) == [], "a missing time_zone key is fine when date_basis names IST (GOOD uses 'completed_at (IST)')."


def test_order_of_messages_and_input_untouched():
    s = {"name": "x", "numerator": "valid jobs", "period": "between 1 and 2"}
    before = copy.deepcopy(s)
    got = lint_definition(s)
    assert got == ["missing: question", "missing: grain", "missing: denominator", "missing: date_basis", "missing: exclusions",
                   "missing: owner", "missing: version",
                   "vague: numerator uses 'valid' without a rule",
                   "closed interval: write the period as start <= t < end",
                   "no time zone: say UTC or IST"], "order: missing, vague, closed interval, time zone. Got %s" % got
    assert s == before, "do not change the spec you were given."
