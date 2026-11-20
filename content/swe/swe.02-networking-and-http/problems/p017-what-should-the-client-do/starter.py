from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def client_action(status, headers, now=None):
    # TODO: lower-case the header names, then follow the table
    return "give-up"
