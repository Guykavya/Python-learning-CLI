"""Monthly sales report. Correct, but far too slow on a year of real data."""
from datetime import datetime


def parse_products(products_csv):
    products = []
    for line in products_csv.strip().splitlines()[1:]:
        pid, name, category, price = line.split(",")
        products.append({"id": pid, "name": name, "category": category, "price": int(price)})
    return products


def find_product(products, pid):
    for product in products:
        if product["id"] == pid:
            return product
    return None


def month_of(date_text):
    return datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y-%m")


def order_lines(orders_csv):
    return orders_csv.strip().splitlines()[1:]


def build_report(products_csv, orders_csv):
    products = parse_products(products_csv)
    count = 0
    skipped = 0
    revenue = 0
    per_product = {}
    months = []
    for line in order_lines(orders_csv):
        order_id, date, pid, qty = line.split(",")
        product = find_product(products, pid)
        if product is None:
            skipped += 1
            continue
        count += 1
        amount = product["price"] * int(qty)
        revenue += amount
        per_product[pid] = per_product.get(pid, 0) + amount
        month = month_of(date)
        if month not in months:
            months.append(month)
    months.sort()

    lines = ["SALES REPORT", f"orders: {count}", f"skipped: {skipped}", f"revenue: {revenue}", "", "BY MONTH"]
    for month in months:
        total = 0
        for line in order_lines(orders_csv):
            order_id, date, pid, qty = line.split(",")
            if month_of(date) == month:
                product = find_product(products, pid)
                if product is not None:
                    total += product["price"] * int(qty)
        lines.append(f"{month}  {total}")

    lines += ["", "TOP PRODUCTS"]
    ranked = []
    for pid, amount in per_product.items():
        order = sorted(per_product, key=lambda p: (-per_product[p], p))
        rank = order.index(pid) + 1
        product = find_product(products, pid)
        ranked.append((rank, f"{rank:>3}. {pid}  {product['name']} ({product['category']})  {amount}"))
    ranked.sort()
    lines += [text for _, text in ranked]
    return "\n".join(lines) + "\n"
