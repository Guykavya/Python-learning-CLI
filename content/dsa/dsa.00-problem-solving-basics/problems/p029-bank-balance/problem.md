# Bank account simulator

Simulate a simple bank account. You are given the opening balance and a list of operations.
Each operation is a letter and an amount:

- `D` means deposit: add the amount to the balance.
- `W` means withdraw: subtract the amount from the balance.

Process the operations in order. For each one, check these rules **in this order** and print exactly one line:

1. If the letter is neither `D` nor `W`: print `unknown operation`. The balance does not change.
2. Else, if the amount is 0 or negative: print `invalid amount`. The balance does not change.
3. Else, if it is a withdrawal and the amount is bigger than the current balance: print `declined`.
   The balance does not change. (Withdrawing exactly the whole balance is allowed.)
4. Otherwise apply the operation and print `balance X`, where `X` is the new balance.

After all operations, print `final X` with the final balance.

## Input

- Line 1: the opening balance (a whole number, 0 or more).
- Line 2: `n`, the number of operations.
- Then each operation takes **two lines**: first the letter, then the amount (a whole number).

Every operation has an amount line, even when its letter is unknown.
Use `input()` without a prompt message. Compare the letter line as a whole, with `==` (for example `op == "D"`).
Letters are case-sensitive: `d` is an unknown operation.

## Output

`n` lines, one per operation as described, then the line `final X`.

## Examples

Input:

```
100
4
W
30
W
100
D
50
W
120
```

Output:

```
balance 70
declined
balance 120
balance 0
final 0
```

Input:

```
10
3
D
-5
X
5
W
0
```

Output:

```
invalid amount
unknown operation
invalid amount
final 10
```

Input with no operations (`5` then `0`) prints only `final 5`.

## Constraints

- `0 <= opening balance <= 1000000000`
- `0 <= n <= 10000`
- Amounts are whole numbers between `-1000000000` and `1000000000`.

## Before you code

Walk through the first example by hand, writing the balance after each operation. Then write your plan as
comments at the top of `solution.py`. Why does the order of the checks matter?
