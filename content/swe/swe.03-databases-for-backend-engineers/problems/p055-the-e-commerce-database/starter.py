import os
import sqlite3

from sqlalchemy import CheckConstraint, ForeignKey, String, create_engine, event, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OutOfStock(ValueError):
    pass


class RestoreFailed(Exception):
    pass


# TODO: Customer, Product, Order, OrderLine (see the statement), then:


def make_engine(path):
    raise NotImplementedError


def seed(session):
    raise NotImplementedError


def place_order(session, customer_id, items):
    raise NotImplementedError


def orders_with_totals(session):
    raise NotImplementedError


def backup(src_path, dst_path):
    raise NotImplementedError


def fingerprint(conn):
    raise NotImplementedError


def restore_and_verify(backup_path, expected, dest_path):
    raise NotImplementedError
