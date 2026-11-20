import os
import sqlite3


class RestoreFailed(Exception):
    pass


def fingerprint(conn):
    # TODO: {table: {"rows": n, "sums": {numeric column: total}}} for every user table
    return {}


def restore_and_verify(backup_path, expected, dest_path):
    # TODO: fresh dest only; integrity_check; restore with backup(); compare fingerprints; RestoreFailed names the tables
    return {}
