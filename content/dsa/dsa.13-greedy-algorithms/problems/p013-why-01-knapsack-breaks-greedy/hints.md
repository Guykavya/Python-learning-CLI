## Hint 1

Greedy breaks when its first, densest item is an **awkward size**: after taking it, the space left is too small for the next items, and it stays empty. Try a capacity like 8 with one dense item of weight 5 and two less dense items of weight 4. Check: what does greedy take, and does anything still fit after it?

## Hint 2

For question 3, read the fractional proof in chapter section 7 again and look for the words "a little" or "any amount". In 0/1 knapsack you can only move whole items; swapping a whole item of weight 4 for one of weight 5 changes the total weight. Does it still fit?

## Hint 3

For question 4: build a tiny instance where the most valuable item is very heavy (it fills the bag alone) and several light items together are worth more. For "lightest first", make the lightest items nearly worthless.
