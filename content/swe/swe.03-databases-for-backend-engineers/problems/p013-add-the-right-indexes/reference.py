INDEXES = [
    "CREATE INDEX idx_orders_customer_status ON orders(customer_id, status)",
    "CREATE INDEX idx_orders_status_created ON orders(status, created)",
]
