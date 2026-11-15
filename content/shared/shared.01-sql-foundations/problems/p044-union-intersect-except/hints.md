## Hint 1

Which operator means "in either list", which "in both", and which "in the first but not in the second"? Does the order of the two
`SELECT`s matter for each of them? Where does a single `ORDER BY` go?

## Hint 2

```
QUERY_A:  SELECT email FROM newsletter  ?  SELECT email FROM buyers  ORDER BY email;
QUERY_B:  SELECT email FROM newsletter  ?  SELECT email FROM buyers  ORDER BY email;
QUERY_C:  SELECT email FROM ?  EXCEPT  SELECT email FROM ?  ORDER BY email;
```
