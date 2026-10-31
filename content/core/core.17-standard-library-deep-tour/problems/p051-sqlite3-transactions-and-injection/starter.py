import sqlite3


def open_bank(path, accounts):
    return sqlite3.connect(path)


def balance(conn, name):
    return 0


def transfer(conn, src, dst, amount):
    pass


def accounts_with_prefix(conn, prefix):
    return []
