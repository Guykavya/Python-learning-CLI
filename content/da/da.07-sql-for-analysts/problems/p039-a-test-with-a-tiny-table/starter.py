import pandas as pd


def retention_on(con, users, events, cutoff):
    """Return [(cohort_month, k, active_users, cohort_size), ...] sorted; only logins before `cutoff` count."""
    raise NotImplementedError


def tiny_case():
    """Return (users_df, events_df, expected_rows): at most 5 users and 12 events, answer counted by hand (cutoff 2025-07-01)."""
    raise NotImplementedError
