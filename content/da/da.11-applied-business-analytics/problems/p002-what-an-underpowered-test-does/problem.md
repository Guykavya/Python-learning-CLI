# What an underpowered test does

Chapter section 2.12. ShopNest ran its banner test with 12,000 visitors per group, about a third of the 36,800 per group the plan called for. To see what that means, the chapter repeated the **same** test
400 times. The true lift is about +0.7 points. The 400 estimates spread from about -0.1 to +1.5 points; only a minority of the tests came out "significant"; and among those, the average estimated lift was
well above +0.7 points. A few runs even showed a lift **below zero**.

In `answer.md`, in about 150 to 250 words, explain to a product manager:

1. why a test with too few visitors usually **misses** a real effect;
2. why the runs that **do** come out significant **overstate** the lift;
3. why some runs get the **sign** wrong;
4. what you should have done before starting.

## Example

A start: "With too few visitors the estimate of the lift is noisy: one run says +1.4 points, the next +0.1, the next -0.2. A real effect of +0.7 points..."
