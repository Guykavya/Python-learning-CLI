from solution import normalise

ROWS = [
    {"order_ref": "A-1", "order_date": "2026-01-05", "customer_email": "asha@x.com", "customer_name": "Asha",
     "product_sku": "TEA", "product_name": "Green Tea", "price_paise": 25000, "qty": 2},
    {"order_ref": "A-1", "order_date": "2026-01-05", "customer_email": "asha@x.com", "customer_name": "Asha",
     "product_sku": "COF", "product_name": "Coffee", "price_paise": 30000, "qty": 1},
    {"order_ref": "A-2", "order_date": "2026-01-09", "customer_email": "asha@x.com", "customer_name": "Asha",
     "product_sku": "TEA", "product_name": "Green Tea", "price_paise": 25000, "qty": 4},
    {"order_ref": "B-1", "order_date": "2026-01-09", "customer_email": "ravi@x.com", "customer_name": "Ravi",
     "product_sku": "TEA", "product_name": "Green Tea", "price_paise": 25000, "qty": 1},
]


def rejoin(t):
    cust = {c["id"]: c for c in t["customers"]}
    prod = {p["id"]: p for p in t["products"]}
    order = {o["id"]: o for o in t["orders"]}
    out = []
    for line in t["order_lines"]:
        o = order[line["order_id"]]
        c = cust[o["customer_id"]]
        p = prod[line["product_id"]]
        out.append({"order_ref": o["ref"], "order_date": o["date"], "customer_email": c["email"],
                    "customer_name": c["name"], "product_sku": p["sku"], "product_name": p["name"],
                    "price_paise": p["price_paise"], "qty": line["qty"]})
    return out


def test_table_sizes_and_columns():
    t = normalise(ROWS)
    assert set(t) == {"customers", "products", "orders", "order_lines"}
    assert (len(t["customers"]), len(t["products"]), len(t["orders"]), len(t["order_lines"])) == (2, 2, 3, 4), (
        "Each customer, product and order is stored ONCE; order_lines has one row per input row.")
    assert set(t["customers"][0]) == {"id", "email", "name"}
    assert set(t["products"][0]) == {"id", "sku", "name", "price_paise"}
    assert set(t["orders"][0]) == {"id", "ref", "date", "customer_id"}
    assert set(t["order_lines"][0]) == {"order_id", "product_id", "qty"}


def test_ids_are_first_seen_order():
    t = normalise(ROWS)
    assert [(c["id"], c["email"]) for c in t["customers"]] == [(1, "asha@x.com"), (2, "ravi@x.com")]
    assert [(p["id"], p["sku"]) for p in t["products"]] == [(1, "TEA"), (2, "COF")]
    assert [(o["id"], o["ref"], o["customer_id"]) for o in t["orders"]] == [(1, "A-1", 1), (2, "A-2", 1), (3, "B-1", 2)]


def test_joining_back_reproduces_every_row():
    assert rejoin(normalise(ROWS)) == ROWS, "The decomposition must be lossless: re-joining gives back the original rows."


def test_no_duplicates_in_any_table():
    t = normalise(ROWS * 3)
    assert len(t["customers"]) == 2 and len(t["products"]) == 2 and len(t["orders"]) == 3
    assert len(t["order_lines"]) == 12


def test_empty_input():
    assert normalise([]) == {"customers": [], "products": [], "orders": [], "order_lines": []}
