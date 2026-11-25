import numpy as np
import pandas as pd
import pytest


def make_messy_sales(path, n=1200, seed=11):
    rng = np.random.default_rng(seed)
    order_id = np.arange(5001, 5001 + n)
    when = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 181, n), unit="D")
    style = rng.choice(3, n, p=[0.6, 0.3, 0.1])                       # three date styles
    date_txt = np.where(style == 0, when.strftime("%Y-%m-%d"),
               np.where(style == 1, when.strftime("%d/%m/%Y"), when.strftime("%b %d, %Y"))).astype(object)
    date_txt[rng.choice(n, 6, replace=False)] = "31/02/2025"          # impossible date
    date_txt[rng.choice(n, 3, replace=False)] = "2035-03-04"          # typo in the year
    date_txt[rng.choice(n, 5, replace=False)] = None                  # missing

    people = np.array(["Asha Rao", "Ben Kumar", "Chitra Singh", "Dev Patel", "Esha Nair", "Farid Khan"])
    cust = rng.choice(people, n)
    mode = rng.choice(4, n, p=[0.7, 0.1, 0.1, 0.1])                   # case and spaces
    cust = np.where(mode == 1, np.char.upper(cust), np.where(mode == 2, np.char.add(cust, "  "),
           np.where(mode == 3, np.char.add(" ", np.char.lower(cust)), cust)))
    cities = np.array(["Pune", "Delhi", "Agra", "Jaipur", "Surat"])
    city = rng.choice(cities, n, p=[0.3, 0.3, 0.15, 0.15, 0.1])
    cm = rng.choice(4, n, p=[0.7, 0.1, 0.1, 0.1])
    city = np.where(cm == 1, np.char.lower(city), np.where(cm == 2, np.char.upper(city),
           np.where(cm == 3, np.char.add(city, " "), city)))

    products = np.array(["rice 5kg", "tea 250g", "novel", "atlas", "puzzle", "robot kit", "spade", "hose pipe"])
    cat_of = dict(zip(products, ["grocery", "grocery", "books", "books", "toys", "toys", "garden", "garden"]))
    base = dict(zip(products, [420.0, 180.0, 350.0, 900.0, 650.0, 2400.0, 520.0, 780.0]))
    prod = rng.choice(products, n)
    category = np.array([cat_of[p] for p in prod])
    category = np.where(rng.random(n) < 0.15, np.char.upper(category), category)

    qty = rng.integers(1, 10, n).astype(object)
    qty[rng.choice(n, 12, replace=False)] = "N/A"
    qty[rng.choice(n, 4, replace=False)] = -1                         # a return typed as a sale?
    qty[rng.choice(n, 3, replace=False)] = 900                        # an extra zero?
    price = np.array([base[p] for p in prod]) * rng.normal(1.0, 0.08, n)
    price[rng.choice(n, 2, replace=False)] *= 100                     # decimal point in the wrong place
    price = price.round(2)
    pm = rng.choice(3, n, p=[0.5, 0.25, 0.25])                        # three money styles
    price_txt = np.where(pm == 0, [f"₹{v:,.2f}" for v in price],
                np.where(pm == 1, [f"Rs. {v:.1f}" for v in price], [f"{v:.2f}" for v in price])).astype(object)
    price_txt[rng.choice(n, 20, replace=False)] = None
    disc = rng.choice([None, "5%", "10%", "0.15"], n, p=[0.55, 0.2, 0.15, 0.1])
    paid = rng.choice(["Yes", "No", "Y", "N", "TRUE", "false", None], n, p=[0.5, 0.1, 0.15, 0.05, 0.1, 0.05, 0.05])

    df = pd.DataFrame({"order_id": order_id, "order_date": date_txt, "customer": cust, "city": city,
                       "product": prod, "category": category, "qty": qty, "unit_price": price_txt,
                       "discount": disc, "paid": paid})
    extra = df.sample(30, random_state=1)                             # 30 exact duplicate rows
    clash = df.sample(5, random_state=2).copy()                       # same id, different quantity
    clash["qty"] = 7
    out = pd.concat([df, extra, clash]).sample(frac=1, random_state=3).reset_index(drop=True)
    out.to_csv(path, index=False)


@pytest.fixture(scope="session")
def messy_csv(tmp_path_factory):
    """The chapter's messy sales file (chapter 19.1): 1,200 orders, 1,235 rows, seed 11."""
    path = tmp_path_factory.mktemp("data") / "sales_raw.csv"
    make_messy_sales(path)
    return path
