# Sort words by length

Read `n` words. Print them sorted by **length**, shortest first. Words with the same length must stay in the order they had in the input
(this is what a **stable** sort gives you for free). Print the words on one line, separated by spaces.

## Input

- Line 1: `n`.
- Line 2: `n` words (lowercase letters).

## Output

One line with the sorted words.

## Constraints

- `1 <= n <= 100000`
- each word has between 1 and 20 letters

## Example

Input:

```
6
pear fig apple kiwi date plum
```

Output:

```
fig pear kiwi date plum apple
```
