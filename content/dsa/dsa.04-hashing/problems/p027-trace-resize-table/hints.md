## Hint 1

Size 4: after 1 key, 0.25; after 2, 0.5; after 3, exactly 0.75 (not greater); after the 4th, 1.0 which is above 0.75, so it resizes.

## Hint 2

Rehash order after the 4th insert: old bucket 0 chain, then bucket 1 chain, and so on. Compute each key modulo 8.

## Hint 3

At size 8 the limit is 6 keys (6/8 = 0.75 is allowed; 7/8 is not), so the second resize happens on the 7th key.
