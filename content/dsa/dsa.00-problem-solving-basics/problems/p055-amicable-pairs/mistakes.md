- Adding the square root twice. For 36, `d = 6` gives `36 // 6 = 6`, the same divisor; adding it
  twice makes the sum wrong for every perfect square.
- Including the number itself in the sum (starting `d` at 1 and pairing it with `a // 1 = a`). Then
  every sum is too big by `a` and no pair is ever found.
- Not checking `b > a`. Every pair is printed twice (`220 284` and later `284 220`), and perfect
  numbers like 6 and 28 appear as "pairs" with themselves.
- Summing divisors by trying every `d` below `a`. For `n = 30000` that is hundreds of millions of
  divisions and it does not finish in time.
