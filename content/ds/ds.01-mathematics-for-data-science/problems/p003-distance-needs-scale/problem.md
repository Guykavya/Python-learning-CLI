# Distance needs scale

Chapter section 1.5. Euclidean distance adds up squared differences, so a column measured in thousands drowns a column measured in tens. Before comparing rows, **standardise** each column: subtract its mean and divide by its standard deviation.

Write two functions, both taking a 2-D array `X` (rows = people, columns = features):

- `standardise(X)` returns a new array in which every column has mean 0 and standard deviation 1 (population std, `ddof=0`). A **constant column** becomes all zeros (no `nan`).
- `distances_from_first(X)` returns a 1-D array with the Euclidean distance from row 0 to each of the **other** rows (so `len(X) - 1` numbers).

## Example

For the columns `[age, income]`: person 0 is `[30, 50000]`, person 1 is `[31, 90000]`, person 2 is `[60, 51000]`, person 3 is `[33, 52000]`. On the raw numbers person 2 looks closest (income differs by only 1,000, age by 30 years); after standardising, person 3 is closest.
