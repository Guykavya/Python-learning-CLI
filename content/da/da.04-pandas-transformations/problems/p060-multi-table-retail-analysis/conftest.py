"""A small, hand-checkable version of the chapter's six retail tables (make_retail column names)."""
import pandas as pd
import pytest


def make_tables():
    customers = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4", "C5", "C6"],
        "city": ["Pune", "Delhi", "Agra", "Pune", "Surat", "Mumbai"],
        "segment": ["retail", "premium", "retail", "business", "retail", "premium"],
        "signup": pd.to_datetime(["2024-03-01", "2024-05-11", "2024-06-30", "2024-09-02", "2024-10-10", "2024-12-24"]),
    })
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"],
        "category": ["grocery", "grocery", "grocery", "grocery", "toys", "toys", "home", "office"],
        "list_price": [50.0, 20.0, 75.0, 200.0, 120.0, 300.0, 90.0, 75.0],
    })
    stores = pd.DataFrame({
        "store_id": ["S1", "S2", "S3"],
        "store_city": ["Pune", "Delhi", "Agra"],
        "region": ["west", "north", "north"],
    })
    orders = pd.DataFrame({
        "order_id": [10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 10010],
        "customer_id": ["C1", "C2", "C9", "C1", "C3", "C2", "C4", "C1", "C3", "C4"],
        "store_id": ["S1", "S2", "S1", "S3", "S2", "S1", "S3", "S2", "S1", "S2"],
        "order_date": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-01-15", "2025-02-02", "2025-02-14",
                                      "2025-02-20", "2025-03-01", "2025-03-09", "2025-03-18", "2025-03-30"]),
        "channel": ["store", "online", "store", "online", "store", "online", "store", "store", "online", "online"],
    })
    items = pd.DataFrame({
        "order_id": [10001, 10001, 10002, 10003, 10003, 10004, 10005, 10005, 10006, 10007, 10007, 10008, 10009,
                     10010, 10010],
        "product_id": ["P1", "P5", "P2", "P1", "P3", "P4", "P2", "P8", "P1", "P3", "P5", "P4", "P2", "P1", "P8"],
        "qty": [2, 1, 3, 1, 4, 1, 2, 1, 1, 2, 2, 1, 5, 3, 2],
        "unit_price": [50.0, 120.0, 20.0, 50.0, 10.0, 200.0, 20.0, 75.0, 45.0, 75.0, 110.0, 180.0, 18.0, 50.0, 75.0],
    })
    returns = pd.DataFrame({
        "order_id": [10001, 10004, 10009],
        "product_id": ["P5", "P4", "P2"],
        "reason": ["changed mind", "damaged", "wrong item"],
        "refund": [1.0, 0.5, 1.0],
    })
    return {"customers": customers, "products": products, "stores": stores,
            "orders": orders, "items": items, "returns": returns}


@pytest.fixture
def tables():
    return make_tables()
