## Approach

The model answer is in `answer.md`. Review in layers: first **correctness and safety** (money, API, tests), then readability, then style. Spend your attention in that order; a formatter can handle the style.

The weight labels (chapter section 16.5) tell the author what is required and what is a choice. A review with no labels forces the author to guess which comments matter.

## Complexity

Not applicable.

## Another way

Before commenting, check out the branch and run the tests yourself (`git switch` and `python tasks.py check`, chapter section 16.2): half of the review questions answer themselves.

## Why it matters

A good review catches the problems that cost the most later (silent API breaks, money errors, missing tests), and is written so the author wants to fix them.
