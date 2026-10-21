# Exact versus close

Read three numbers `a`, `b` and `c` (decimals allowed). Print:

```
Exact: <is a + b exactly equal to c?>
Close: <is a + b close to c?>
```

For "close", use `math.isclose(a + b, c, abs_tol=1e-9)`. The `abs_tol` part makes it work
when `c` is zero.

**Example**

Input:
```
0.1
0.2
0.3
```
Output:
```
Exact: False
Close: True
```
