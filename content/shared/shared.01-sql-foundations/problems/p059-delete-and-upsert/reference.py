SCRIPT = """
DELETE FROM stock WHERE qty = 0;

INSERT INTO stock (book_id, qty)
SELECT book_id, SUM(qty) FROM incoming GROUP BY book_id
ON CONFLICT (book_id) DO UPDATE SET qty = qty + excluded.qty;
"""
