# Counting with combinations

Chapter section 9.2. The chance of exactly `k` heads in `n` fair coin flips is the number of ways to choose which flips are heads, `C(n, k)`, divided by the number of equally likely outcomes, `2**n`.

Write `p_exactly_k_heads(n, k)` using `math.comb`. For `k` outside `0..n` the probability is `0.0`.

## Example

```text
p_exactly_k_heads(2, 1)   ->  0.5      (HT or TH out of HH, HT, TH, TT)
p_exactly_k_heads(10, 5)  ->  0.24609375
```
