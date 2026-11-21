import csv
import io
from collections import defaultdict
from email.message import EmailMessage


class FakeTransport:
    """Stands in for smtplib. Tests and dry runs use this; production uses the real one."""

    def __init__(self):
        self.sent = []

    def send_message(self, msg):
        self.sent.append(msg)


def summarize(csv_text):
    """(totals per region sorted by region, line numbers of bad rows). Bad rows are reported, not hidden."""
    totals, bad = defaultdict(float), []
    for line_no, row in enumerate(csv.DictReader(io.StringIO(csv_text)), start=2):   # line 1 is the header
        try:
            region = row["region"].strip()
            if not region:
                raise ValueError("missing region")
            amount = float(row["amount"])          # convert BEFORE touching totals: a failed row must leave no trace
            totals[region] += amount
        except (KeyError, ValueError, TypeError, AttributeError):
            bad.append(line_no)
    return dict(sorted(totals.items())), bad


def build_email(totals, bad_lines, sender, to):
    grand = sum(totals.values())
    lines = [f"{region:10} {amount:10,.2f}" for region, amount in totals.items()]
    lines.append(f"{'TOTAL':10} {grand:10,.2f}")
    if bad_lines:
        lines.append(f"\nWarning: could not read line(s) {bad_lines}. Please check the export.")
    msg = EmailMessage()
    msg["Subject"] = f"Weekly sales: {grand:,.2f}"
    msg["From"], msg["To"] = sender, to
    msg.set_content("\n".join(lines))
    return msg


def send(msg, transport):
    transport.send_message(msg)
