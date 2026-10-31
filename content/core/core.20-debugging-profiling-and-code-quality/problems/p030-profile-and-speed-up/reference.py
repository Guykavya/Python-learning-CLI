"""Monthly sales report: same output as the original, each order is looked at once."""


def parse_products(products_csv):
    products = {}
    for line in products_csv.strip().splitlines()[1:]:
        pid, name, category, price = line.split(",")
        products[pid] = {"id": pid, "name": name, "category": category, "price": int(price)}
    return products


def build_report(products_csv, orders_csv):
    products = parse_products(products_csv)          # dict: O(1) lookup by id
    count = 0
    skipped = 0
    revenue = 0
    per_product = {}
    per_month = {}
    for line in orders_csv.strip().splitlines()[1:]:  # one pass over the orders
        _order_id, date, pid, qty = line.split(",")
        product = products.get(pid)
        if product is None:
            skipped += 1
            continue
        count += 1
        amount = product["price"] * int(qty)
        revenue += amount
        per_product[pid] = per_product.get(pid, 0) + amount
        month = date[:7]                              # "YYYY-MM-DD" -> "YYYY-MM"
        per_month[month] = per_month.get(month, 0) + amount

    lines = ["SALES REPORT", f"orders: {count}", f"skipped: {skipped}", f"revenue: {revenue}", "", "BY MONTH"]
    for month in sorted(per_month):
        lines.append(f"{month}  {per_month[month]}")

    lines += ["", "TOP PRODUCTS"]
    order = sorted(per_product, key=lambda p: (-per_product[p], p))   # sort once
    for rank, pid in enumerate(order, start=1):
        product = products[pid]
        lines.append(f"{rank:>3}. {pid}  {product['name']} ({product['category']})  {per_product[pid]}")
    return "\n".join(lines) + "\n"
