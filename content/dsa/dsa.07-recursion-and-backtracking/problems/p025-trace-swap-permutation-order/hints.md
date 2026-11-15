## Hint 1

Line 1: position 0 keeps 1 (swap 0 with 0). The rest `[2, 3, 4]` follows the 3-item pattern `abc acb bac bca cba cab`.

## Hint 2

Line 2: swap position 0 with position 1, so the list is `[2, 1, 3, 4]`; apply the pattern to `[1, 3, 4]`. Line 3: back to `[1, 2, 3, 4]`, then swap 0 with 2: `[3, 2, 1, 4]`.

## Hint 3

Line 4: swap 0 with 3 on `[1, 2, 3, 4]` gives `[4, 2, 3, 1]`; apply the pattern to `[2, 3, 1]`.
