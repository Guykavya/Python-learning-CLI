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
    # TODO
    return {}, []


def build_email(totals, bad_lines, sender, to):
    # TODO: Subject, From, To and the body described in problem.md
    return EmailMessage()


def send(msg, transport):
    # TODO
    pass
