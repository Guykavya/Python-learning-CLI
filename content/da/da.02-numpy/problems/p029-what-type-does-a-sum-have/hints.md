## Hint 1

Sort the lines into two groups: **aggregations** (`sum`, `mean`, `cumsum`) and **element-wise arithmetic** (`small + small`). Which group gets a wider accumulator automatically, and which keeps `uint8`?

## Hint 2

Rules from Ch. 10.6 and Ch. 4:

```text
sum of bool            -> counts the Trues, int64
sum / cumsum of int8/int16/int32 -> int64;  of uint8/uint16/uint32 -> uint64
mean of integers       -> float64
sum(dtype=np.uint8)    -> accumulator forced to uint8: result mod 256
uint8 + uint8          -> uint8, each element mod 256
float32 sum            -> stays float32
```
