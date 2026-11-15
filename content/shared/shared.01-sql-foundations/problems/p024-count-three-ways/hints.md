## Hint 1

Which part of each count decides what is counted: the rows, the non-NULL values, or the different values?
Look at the table: how many NULL cities are there, and which city repeats?

## Hint 2

```
SELECT COUNT(?)            AS total_rows,        -- rows: use the star
       COUNT(city)         AS with_city,         -- skips NULL
       COUNT(DISTINCT ?)   AS distinct_cities    -- different non-NULL values
FROM customers;
```
