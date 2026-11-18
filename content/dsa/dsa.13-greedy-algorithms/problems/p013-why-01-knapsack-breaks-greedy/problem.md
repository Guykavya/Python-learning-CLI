# Explain: why 0/1 knapsack breaks greedy

Fractional knapsack (chapter section 7, p012) and 0/1 knapsack (section 8) differ by one word: in 0/1 knapsack each item is taken **whole or not at all**. The density greedy is correct for the first and wrong for the second.

Write a short explanation (8 to 12 sentences) in `answer.md` that answers:

1. Give a **concrete** 0/1 instance, with a capacity and at most four items written as `(value, weight)`, where "highest value per kilogram first" does **not** find the best total. Use your own numbers, not the chapter's two examples. Show greedy's choice and total, and the best choice and total.
2. In your instance, what happens to the bag's **empty space**? Why is that space the exact loss?
3. Recall the exchange step that proves fractional knapsack: "remove `d` kilograms of a thinner item, add `d` kilograms of a denser one". Which word of that step is illegal in 0/1 knapsack, and what goes wrong if you try to swap **whole** items instead?
4. Is "highest value first" or "lightest first" a fix? Answer with one sentence and an instance (or a reason).
5. What do you use instead for an exact answer? What is the cheap greedy **approximation** the chapter mentions, and what does it guarantee?

## Example of the level of detail wanted

"Capacity 10. Items A = (10, 6), B = (7, 5), C = (7, 5). Densities 1.67, 1.4, 1.4. Greedy takes A, then neither B nor C fits (6 + 5 = 11 > 10): total 10. Best: B + C, weight 10, total 14." (This is the chapter's example; build a different one.)

Then compare with the model answer and rate yourself.
