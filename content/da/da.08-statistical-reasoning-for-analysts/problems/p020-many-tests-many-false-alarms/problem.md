# Many tests, many false alarms

Chapter section 5.4. If you run `k` independent tests at level 0.05 and **no** effect exists, the chance of **at least one** false
alarm is `1 - 0.95^k`. The simplest protection (Bonferroni) tests each at `0.05 / k`.

```python
for k in (1, 5, 20, 100):
    print(f"k = {k:3d}  P(at least one false alarm) = {1 - 0.95 ** k:.3f}  Bonferroni threshold = {0.05 / k:.4f}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. (Use a calculator for the powers; the point is
the formatting and the pattern.)

Do not run the code before you have written your answer.

## Example

For `k = 2` the line would be `k =   2  P(at least one false alarm) = 0.098  Bonferroni threshold = 0.0250`.

## After you answer

- How many "significant" results do you expect among 100 tests of nothing at 0.05?
- What is the price of the Bonferroni threshold (what gets harder)?
