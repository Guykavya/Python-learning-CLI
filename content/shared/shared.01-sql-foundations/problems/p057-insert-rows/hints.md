## Hint 1

For step 2, which query gives each city exactly once and without the NULL? What clause removes duplicates and which condition removes NULL (remember `= NULL` never matches)?

## Hint 2

```
INSERT INTO customers (name, city, joined) VALUES ('Zoe','Lima','2024-05-01'), ('Yan', NULL, '2024-05-02');
INSERT INTO city_list (city) SELECT DISTINCT city FROM customers WHERE city IS NOT NULL;
```
