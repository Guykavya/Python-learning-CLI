# Palindrome, ignoring punctuation and case

A sentence is a **palindrome** here if it reads the same forwards and backwards after you

- keep only letters and digits (`ch.isalnum()` is `True`), and
- treat upper and lower case as the same letter.

So `"A man, a plan, a canal: Panama"` is a palindrome, and `"race a car"` is not (`raceacar` backwards is `racaecar`).

Check it with **two pointers**: `i` from the left, `j` from the right. Skip any character that is not a letter or
digit, compare the two lowercased characters, and move both pointers inwards.

## Input

- Line 1: `t`, the number of lines to check.
- Next `t` lines: one sentence each (it may contain spaces and punctuation, and it may be empty).

## Output

For each sentence, `yes` or `no` on its own line.

## Example

Input:

```
4
A man, a plan, a canal: Panama
race a car
No 'x' in Nixon
,.!
```

Output:

```
yes
no
yes
yes
```

The last line has no letters or digits at all. An empty string reads the same both ways, so the answer is `yes`.

## Constraints

- `1 <= t <= 100`
- Each line has at most 200000 characters, all of them plain ASCII.
