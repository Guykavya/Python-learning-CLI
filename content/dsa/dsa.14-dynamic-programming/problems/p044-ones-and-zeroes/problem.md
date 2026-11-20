# Ones and zeroes (2-D knapsack)

You get a list of binary strings `strs` and two budgets: at most `m` zeros and at most `n` ones in total. Choose as **many strings as possible** (each string at most once) so that, counted over all chosen strings, there are at most `m` characters `'0'` and at most `n` characters `'1'`. Write `find_max_form(strs, m, n)` that returns that largest number of strings.

## Example

```python
>>> find_max_form(["10", "0001", "111001", "1", "0"], 5, 3)
4
>>> find_max_form(["10", "0", "1"], 1, 1)
2
>>> find_max_form(["00", "000"], 1, 10)
0
>>> find_max_form(["0", "0", "1", "1"], 2, 2)
4
```

In the first example `{"10", "0001", "1", "0"}` uses 5 zeros and 3 ones. In the second, `{"0", "1"}` uses one of each; `"10"` and anything else would need two zeros or two ones.

## Constraints

- `1 <= len(strs) <= 300`, each string has 1 to 10 characters, `0 <= m, n <= 60`.
- Time about `O(len(strs) * m * n)`. Trying all subsets does not finish for 300 strings.

## Think about

This is the 0/1 knapsack of chapter section 10, but the bag has **two** capacities (zeros and ones) and every item has value 1. What is the state now? In the one-array version, why must **both** capacity loops go downwards?
