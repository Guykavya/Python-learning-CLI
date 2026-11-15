SCRIPT = """
CREATE INDEX idx_orders_cust_date   ON orders(customer_id, ordered);
CREATE INDEX idx_orders_status_date ON orders(status, ordered);
CREATE UNIQUE INDEX idx_customers_email ON customers(email);
"""
