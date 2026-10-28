from pathlib import Path

FILES = {
    "invoices/__init__.py": """from .totals import invoice_total
""",
    "invoices/money.py": """from .totals import TAX_RATE


def fmt(amount):
    return f"Rs {amount:.2f}"


def with_tax(amount):
    return amount * (1 + TAX_RATE)
""",
    "invoices/totals.py": """from money import fmt, with_tax

TAX_RATE = 0.18


def invoice_total(items):
    subtotal = sum(price * qty for price, qty in items)
    return fmt(with_tax(subtotal))
""",
    "json.py": """def sample_items():
    return [(100, 2), (50, 1)]
""",
    "report.py": """import json

from invoices import invoice_total

items = json.sample_items()
print(invoice_total(items))
print(json.dumps({"lines": len(items)}))
""",
}


def write_app(root):
    for rel, text in FILES.items():
        target = Path(root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
