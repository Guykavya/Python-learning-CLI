# Fix the slow visitor log

A website logs the user number of every visit, in order. `starter.py` processes the log and prints three lines:

```
served <number of visits>
new users <number of different users>
repeat visits <visits by a user who had visited before>
```

The output is **correct**, but on a log of 300000 visits the program runs for more than half a minute. Your job
is to find **every** slow operation in it, explain to yourself why each one is slow, and fix them so the output
stays exactly the same.

Do not rewrite from scratch. Read the starter line by line and ask of each line: "how much does this cost, and how
many times does it run?"

## Input

- Line 1: `n`.
- Line 2: `n` user numbers.

## Output

Three lines, exactly as shown above.

## Example

Input:

```
6
5 3 5 5 9 3
```

Output:

```
served 6
new users 3
repeat visits 3
```

## Constraints

- `1 <= n <= 300000`
- user numbers are between `1` and `10^9`

Use `input()` without a prompt message.

## Before you code

There are two different slow spots. One of them is slow only when there are many different users. The other is
slow even if there is only one user. Which is which?
