- Off-by-one at block edges: using `k >= length * count` skips a block one digit too early, so
  `k = 9` lands in the 2-digit block. Always test the last digit of a block (9, 189, 2889) and the
  first digit of the next (10, 190, 2890).
- Using `k // length` instead of `(k - 1) // length`. Because `k` counts from 1, the digits of the
  first number are positions 1..length, and `k // length` moves to the next number one digit too soon.
- Taking `number % 10` without dropping the digits to its right first. That always gives the last
  digit of the number, so `k = 10` prints 0 instead of 1.
- Walking number by number and counting digits. Correct, but for `k = 10^18` it needs about 10^17
  steps.
