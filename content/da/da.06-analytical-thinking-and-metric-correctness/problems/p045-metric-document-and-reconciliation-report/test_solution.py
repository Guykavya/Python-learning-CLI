import re

import pandas as pd
import pytest

from conftest import MetricSpec, make_tables
from solution import definition_doc, reconciliation_report

FEB = ("2025-02-01", "2025-03-01")

# Counted by hand from the comments in conftest.py (see the rows of JOBS, PAYMENTS, REFUNDS).
FEB_REPORT = """# Reconciliation report: 2025-02-01 to 2025-03-01 (IST)

## 1. Total volume against completed volume

step | change | running | check
total volume (created in month) |  | 7 |
created in month, cancelled (never started) | -1 | 6 |
created in month, failed | -1 | 5 |
created in month, pending (no start date yet) | -1 | 4 |
created in month, started after the month | -1 | 3 |
created before the month, started in it | +1 | 4 |
= completed volume (started in month) |  | 4 | OK

Jobs behind each line:
- created in month, cancelled (never started): [3]
- created in month, failed: [4]
- created in month, pending (no start date yet): [6]
- created in month, started after the month: [5]
- created before the month, started in it: [2]

## 2. Completed work against net cash

step | change | running | check
completed value (month) |  | 5300 |
completed in month, paid before the month | -500 | 4800 |
completed in month, paid after the month | -1500 | 3300 |
completed in month, not paid yet | -800 | 2500 |
paid in month, job completed earlier | +1000 | 3500 |
paid in month, job completed later or pending | +500 | 4000 |
paid in month, other jobs | +100 | 4100 |
refunds issued in month | -400 | 3700 |
= net cash (month) |  | 3700 | OK

Jobs behind each line:
- completed in month, paid before the month: [1]
- completed in month, paid after the month: [10]
- completed in month, not paid yet: [9]
- paid in month, job completed earlier: [8]
- paid in month, job completed later or pending: [5, 6]
- paid in month, other jobs: [3]
- refunds issued in month: [1, 10]"""

FIELDS = ["Question", "Unit", "Date basis", "Includes", "Excludes"]


# ---- Part 1: the definition document -------------------------------------------------------------------------------

def test_document_header(specs):
    doc = definition_doc(specs)
    lines = doc.split("\n")
    assert lines[0] == "# QuickFix: metric definitions (v1)", "the first line is the title. Got %r." % lines[0]
    assert lines[2] == "All dates are IST (UTC+05:30). A month is a half-open interval [first day, first day of next month).", (
        "the third line states the time zone and the half-open month. Got %r." % lines[2])
    assert lines[1] == "" and lines[3] == "", "an empty line after the title and after the note."


def test_every_metric_section_has_all_the_fields_in_order(specs):
    doc = definition_doc(specs)
    sections = doc.split("### ")[1:]
    assert [s.split("\n")[0] for s in sections] == [m.name for m in specs], "one '### <name>' section per metric, in the order of the list."
    for spec, section in zip(specs, sections):
        lines = section.split("\n")
        want = [f"- {f}: {getattr(spec, attr)}" for f, attr in zip(FIELDS, ["question", "unit", "date_basis", "includes", "excludes"])]
        assert lines[1:6] == want, ("section %s must list Question, Unit, Date basis, Includes, Excludes as '- Field: value' lines, "
                                    "in this order. Got %s." % (spec.name, lines[1:6]))


def test_document_text_exactly(specs):
    doc = definition_doc(specs[:1])
    want = ("# QuickFix: metric definitions (v1)\n\n"
            "All dates are IST (UTC+05:30). A month is a half-open interval [first day, first day of next month).\n\n"
            "### jobs_created\n- Question: How much demand arrived?\n- Unit: jobs\n- Date basis: created_at (IST)\n"
            "- Includes: all statuses\n- Excludes: none\n")
    assert doc == want, "the text must match exactly (each section ends with an empty line, so the text ends with a newline). Got %r." % doc


def test_document_works_for_any_specs():
    other = [MetricSpec("a", "qa", "ua", "da", "ia", "ea", None), MetricSpec("b", "qb", "ub", "db", "ib", "eb", None)]
    doc = definition_doc(other)
    assert doc.count("### ") == 2 and "### b\n- Question: qb\n- Unit: ub\n- Date basis: db\n- Includes: ib\n- Excludes: eb\n" in doc, (
        "the document is built from the specs you are given, nothing is hard-coded.")
    assert definition_doc([]).endswith("next month).\n"), "no specs: only the header (title, empty line, note, empty line)."


# ---- Part 2: the reconciliation report -----------------------------------------------------------------------------

def test_february_report_matches_the_hand_count(tables):
    got = reconciliation_report(tables, FEB)
    assert got == FEB_REPORT, ("the report must match the hand-counted text exactly. First difference:\n%s" % _first_difference(got, FEB_REPORT))


def _first_difference(got, want):
    for i, (a, b) in enumerate(zip(got.split("\n"), want.split("\n"))):
        if a != b:
            return "line %d: got %r, expected %r" % (i + 1, a, b)
    return "lengths differ: got %d lines, expected %d" % (len(got.split("\n")), len(want.split("\n")))


def _bridges(report):
    """The two bridge tables of a report as lists of (label, change or None, running or None, check)."""
    out, current = [], None
    for line in report.split("\n"):
        if line.startswith("step | change"):
            current = []
            out.append(current)
        elif current is not None and line == "":
            current = None
        elif current is not None:
            text = line[:-2] + " | " if line.endswith(" |") else line       # an empty last cell leaves only ' |'
            current.append([c.strip() for c in text.split(" | ")])
    return out


@pytest.mark.parametrize("month", [("2025-03-01", "2025-04-01"), ("2025-01-01", "2025-02-01"), ("2024-12-01", "2025-01-01")])
def test_bridges_close_for_other_months(tables, month):
    report = reconciliation_report(tables, month)
    assert "UNEXPLAINED" not in report, "a bridge must close: no UNEXPLAINED in the report."
    bridges = _bridges(report)
    assert len(bridges) == 2, "the report has two bridge tables (found %d)." % len(bridges)
    for table in bridges:
        assert table[-1][-1] == "OK" and table[-1][0].startswith("= "), "the last line of each bridge is '= <end label> |  | <value> | OK'."
        running = int(table[0][2])
        for cells in table[1:-1]:
            running += int(cells[1])
            assert running == int(cells[2]), "running total after %r must be the previous total plus the change (%d). Got %s." % (cells[0], running, cells[2])
        assert running == int(table[-1][2]), "the last running total %d must equal the end value %s." % (running, table[-1][2])
    assert len(bridges[1]) == 9, "the cash bridge always has the start line, seven steps and the end line (9 lines). Got %d." % len(bridges[1])


def test_empty_month_has_none_lines(tables):
    report = reconciliation_report(tables, ("2024-12-01", "2025-01-01"))
    assert report.count("- none") == 1 or report.count("- none") == 2, "a section with no job behind any line says '- none'."
    first = report.split("## 2.")[0]
    assert "- none" in first, "bridge 1 of an empty month has no steps and no jobs: '- none'. Got:\n%s" % first


def test_march_numbers_by_hand(tables):
    report = reconciliation_report(tables, ("2025-03-01", "2025-04-01"))
    # created in March: none. Completed and started in March: job 5 (started exactly at the start). Work completed in March: job 5 (1500).
    assert "total volume (created in month) |  | 0 |" in report and "created before the month, started in it | +1 | 1 |" in report, (
        "March: no job was created in March, but job 5 (started exactly on 1 March) is completed volume: +1.")
    assert "completed value (month) |  | 1500 |" in report, "work completed in March: job 5 (1,500). Got:\n%s" % report


def test_tables_are_not_changed(tables, specs):
    before = make_tables()
    reconciliation_report(tables, FEB)
    for name in before:
        pd.testing.assert_frame_equal(tables[name], before[name])
    assert re.search(r"^# QuickFix", definition_doc(specs)) is not None
