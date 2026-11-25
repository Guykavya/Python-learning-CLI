## Hint 1

Start from one row per user with the first time of each step (the previous problem). What does `t_cart >= t_view` give when the user never carted? How would you count the users who satisfy the whole chain for step 3 or step 4 in one query, in four columns or four rows?

## Hint 2

```text
f : first time of each step per user (min ... FILTER)
step 1: count(*) FILTER (WHERE t_view IS NOT NULL)
step 2: count(*) FILTER (WHERE t_cart >= t_view)
step 3: count(*) FILTER (WHERE t_checkout >= t_cart AND t_cart >= t_view)
step 4: count(*) FILTER (WHERE t_purchase >= t_checkout AND t_checkout >= t_cart AND t_cart >= t_view)
stack the four counts with UNION ALL, giving each a step number and name
```
