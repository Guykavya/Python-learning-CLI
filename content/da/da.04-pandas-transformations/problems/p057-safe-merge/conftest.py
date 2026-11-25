"""Small inline retail tables (chapter column names) shared by the tests."""
import pandas as pd
import pytest


@pytest.fixture
def orders():
    return pd.DataFrame({
        "order_id": [10001, 10002, 10003, 10004, 10005, 10006],
        "customer_id": ["C1", "C2", "C1", "C9", "C3", None],
        "store_id": ["S1", "S2", "S1", "S3", "S2", "S1"],
        "channel": ["store", "online", "store", "store", "online", "store"],
    })


@pytest.fixture
def customers():
    return pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4"],
        "city": ["Pune", "Delhi", "Agra", "Surat"],
        "segment": ["retail", "premium", "retail", "business"],
    })


@pytest.fixture
def items():
    return pd.DataFrame({
        "order_id": [10001, 10001, 10002, 10003, 10004, 10005, 10006],
        "product_id": ["P1", "P2", "P1", "P3", "P2", "P9", "P3"],
        "qty": [2, 1, 1, 3, 1, 2, 1],
        "revenue": [200.0, 55.5, 100.0, 90.0, 55.5, 80.0, 30.0],
    })


@pytest.fixture
def products():
    return pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4"],
        "category": ["grocery", "home", "toys", "office"],
        "list_price": [100.0, 55.5, 30.0, 12.0],
    })


@pytest.fixture
def returns():
    return pd.DataFrame({
        "order_id": [10001, 10003],
        "product_id": ["P2", "P3"],
        "reason": ["damaged", "changed mind"],
        "refund": [1.0, 0.5],
    })
