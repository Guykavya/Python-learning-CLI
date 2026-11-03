SCRIPT = """
INSERT INTO customers (name, city, joined)
VALUES ('Zoe', 'Lima', '2024-05-01'), ('Yan', NULL, '2024-05-02');

INSERT INTO city_list (city)
SELECT DISTINCT city FROM customers WHERE city IS NOT NULL;
"""
