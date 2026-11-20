## Approach

Real output of the program above (run with the course environment, FastAPI 0.162 and Python 3.14):

```text
1: 401 login required
2: 401 login required
3: 404 order not found
4: 403 admins only
5: 404 order not found
6: 200 ada
```

- **1 and 2: `401 login required`.** `current_user` runs before the route body. An empty header and an unknown token both give `TOKENS.get(...) is None`: "I do not know who you are". Section 7.5: `401` means missing or invalid credentials.
- **3: `404 order not found`.** The token is valid (bo), order 1 exists but belongs to ada. The condition treats "missing" and "not yours" the same way, so the client cannot tell them apart.
- **4: `403 admins only`.** The caller is known (ada) and the endpoint exists for everybody to see; only the permission is missing. Nothing secret is revealed by saying so.
- **5: `404 order not found`.** The order does not exist. Same answer as request 3, on purpose.
- **6: `200 ada`.** Her own order; the function returns the order and the program prints its `owner`.

The program has no random or time-dependent output.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Make a table with the columns "who is it?" (unknown / known), "does the object exist?", "may they?" and fill in the status for each combination. The two `404` cases and the two `401` cases show up as merged rows, which is the whole design.
