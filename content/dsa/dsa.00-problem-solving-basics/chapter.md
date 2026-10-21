# dsa.00 Problem-solving basics

## Why this chapter exists

There is a difference between *recognising* a solution and *producing* one. If you have been
writing code by asking a tool, copying a snippet and adjusting it until it runs, you have
been practising recognition. You can read the code and it makes sense. But when a blank file
is in front of you and nobody is there to help, nothing comes out. That is not a talent
problem. It is a practice problem: you have not yet practised the steps that happen *before*
the code.

Experienced programmers do not stare at a problem and wait for code to appear. They follow a
process, often so quickly that it looks like magic from outside. They read carefully, they
try small cases on paper, they notice a pattern, they write the steps in plain words, and only
then do they type. When the code is wrong, they do not change random things. They trace what
the program actually does and compare it with what it should do.

This chapter teaches that process slowly and explicitly. Every idea here is something you can
practise on paper, without a computer. Every problem in this module is designed to exercise
one part of it. If you follow the process honestly for the next sixty problems, by the end you
will be able to solve small logic problems in your head, and you will have a method for the
larger ones.

You already know the Python you need: `input()`, `print()`, numbers, `if`, `while`, `for`,
`range`, `break`, `continue` and nested loops. This module adds no new syntax. It adds thinking.

A rule for this whole module: **no answer is finished until you have tested it by hand on at
least one example and on at least one edge case.** You will see why soon.

## The process at a glance

Here is the whole process. The rest of the chapter explains each step.

1. **Read** the problem slowly. Find the input, the output and the constraints.
2. **Restate** it in your own words, in one or two sentences.
3. **Work small examples by hand**, including the ones given and some of your own.
4. **Break it into steps** and write them as pseudocode (plain-language steps).
5. **Write the code** from the pseudocode, one step at a time.
6. **Dry run** the code on a small example with a trace table.
7. **Test edge cases**: zero, one, negative, the largest value, empty input.
8. **Debug** by printing state, never by guessing.

It looks long. For a small problem, steps 1 to 4 take two or three minutes, and they save
twenty minutes of confused typing. For a hard problem, they are the only way in.

## Step 1: Reading a problem

Most wrong answers from beginners are not coding mistakes. They are reading mistakes: the
program solves a slightly different problem from the one that was asked. So the first skill is
reading like a lawyer reads a contract, looking for exactly what is promised and what is not.

Every problem has three parts. Find all three before you do anything else.

### The input

What comes in, in what order, and in what form?

- Is it one number or several? Each on its own line, or several on one line?
- Is there a count first ("the first line contains n, then n lines follow")?
- Can a value be zero? Negative? Is it an integer or can it have a decimal point?
- Is there a stop signal, like "the input ends with a line containing 0"?

Write the input format down. For example: "line 1: integer n; then n lines, each one integer."

### The output

What exactly must be printed?

- One line or many? One value per line, or several separated by spaces?
- Exact words and capital letters: `"YES"` and `"Yes"` are different answers to a computer.
- Decimals: how many places? `3.5` and `3.50` are different strings.
- What should be printed in special cases, such as "print `none` if there is no answer"?

Automatic checkers compare your output character by character. A program that computes the
right number but prints `Answer: 42` instead of `42` is wrong. This feels unfair at first. It
is actually useful training: it forces you to read precisely.

### The constraints

Constraints are the limits on the input, such as `1 <= n <= 10^6` or `0 <= a, b <= 10^18`.
Beginners skip them. Strong problem solvers read them first, because constraints tell you two
things:

1. **Which edge cases exist.** If `0 <= n`, then `n = 0` is a legal input and your program must
   handle it. If `n >= 1`, you do not need to worry about zero.
2. **How fast your program must be.** This is the hidden hint in almost every problem.

A useful rule of thumb: plain Python performs roughly ten million simple steps per second
(somewhere between a few million and a few tens of millions, depending on the step). Most
practice sites give one or two seconds. So:

| If n can be as large as | A loop that runs about n times is | What you probably need |
|---|---|---|
| 1,000 | instant | anything, even a loop inside a loop |
| 100,000 | fine | one loop; a loop inside a loop (n times n = 10^10) is far too slow |
| 10,000,000 | borderline in Python | one simple loop, nothing extra inside it |
| 10^12 | impossible (hours) | a loop up to the square root (10^6 steps), or a formula |
| 10^18 | impossible (centuries) | a formula, or a loop that halves or divides the number each step |

When a problem says `n <= 10^18`, it is telling you: "do not loop from 1 to n". When it says
`n <= 1000`, it is telling you: "the simple way is fine, do not over-think it."

### A reading example

> Read a positive integer n (1 <= n <= 10^12). Print `prime` if n is prime and `not prime`
> otherwise.

- Input: one integer on one line. It is at least 1, so 1 is a legal input (and 1 is not prime,
  a classic trap). No negatives.
- Output: exactly `prime` or `not prime`, lower case, one line.
- Constraints: n up to 10^12. A loop from 2 to n would run a trillion times. That is too slow.
  So I already know before I start that I need something faster. (Later in this chapter you
  will see that checking divisors up to the square root is enough: 10^6 steps.)

Notice how much you learned before writing any code.

## Step 2: Restating the problem

Now say the problem back in your own words, in one or two sentences, as if explaining it to a
friend. Write it as a comment at the top of your file.

A restatement is not a copy. Copying keeps the problem's wording, which might hide what it is
really asking. Restating forces you to understand it. If you cannot restate it, you do not yet
understand it, and no amount of coding will fix that.

Example. The original:

> A number is called "balanced" if the sum of the digits in its odd positions (counting from
> the right, starting at 1) equals the sum of the digits in its even positions. Given n, report
> whether n is balanced.

A restatement:

> Walk through the digits of n from the right. Add the 1st, 3rd, 5th, ... digits into one
> total and the 2nd, 4th, 6th, ... into another. Print whether the two totals are equal.

The restatement already contains the plan: "walk through the digits from the right" means the
`% 10` and `// 10` pattern, and "two totals" means two accumulators.

## Step 3: Working small examples by hand

This is the step that separates people who can solve problems from people who cannot. Before
you think about code, **solve the problem yourself, by hand, for small inputs**. If you cannot
solve it by hand, you cannot tell a computer how to solve it.

Do this:

1. Work through the examples given in the problem, by hand, and check that you get the same
   answers. If you do not, you have misread something. Go back to Step 1.
2. Invent two or three of your own small examples, including at least one tricky one.
3. While you do it, **watch what you are doing**. The steps your hands and eyes take are the
   algorithm. Your job afterwards is just to write them down.

Example: for the "balanced number" problem, take n = 1452.

- Digits from the right: 2 (position 1), 5 (position 2), 4 (position 3), 1 (position 4).
- Odd positions: 2 + 4 = 6. Even positions: 5 + 1 = 6. Equal, so balanced.

What did I do? I took digits one at a time from the right, and I kept track of whether I was
at an odd or even position. I switched between the two totals each time. That is the whole
algorithm.

Now a tricky case: n = 7. Odd total 7, even total 0. Not balanced. And n = 0? One digit, 0.
Odd total 0, even total 0. Balanced? That depends on the problem's rules. A careful reader
notices and checks.

### When the answer is not obvious, make a table

For problems that ask "what is the answer for n?", compute the answer for n = 1, 2, 3, ... up
to 8 or 10 in a table. Patterns jump out of tables that never appear in your head.

Example: what is `1 - 2 + 3 - 4 + ... (+ or -) n`?

| n | sum |
|---|---|
| 1 | 1 |
| 2 | -1 |
| 3 | 2 |
| 4 | -2 |
| 5 | 3 |
| 6 | -3 |

Look at the table: for even n the answer is `-n/2`, and for odd n it is `(n+1)/2`. A loop
would work for small n, but now you have a formula that works instantly even for n = 10^18.
You found it with a pencil, not with code.

<details><summary>Try it: fill the table for "sum of the first n odd numbers" (1, 1+3, 1+3+5, ...) for n = 1 to 5. What is the pattern?</summary>

| n | sum |
|---|---|
| 1 | 1 |
| 2 | 4 |
| 3 | 9 |
| 4 | 16 |
| 5 | 25 |

The sum of the first n odd numbers is n * n. You would never guess that without the table.
</details>

## Step 4: Breaking the problem into steps

Once you can solve it by hand, write down the steps you took, in order, in plain words. This
is **pseudocode**: code-shaped English. It has no fixed syntax. It just needs to be precise
enough that someone could follow it without thinking.

Good pseudocode:

- Uses one line per action.
- Names the things you track ("total", "count", "largest so far").
- Shows repetition clearly ("repeat while n is greater than 0") and decisions clearly
  ("if the digit is even ...").
- Says what is printed at the end.

For the balanced-number problem:

```text
read n
make it non-negative
odd_total = 0, even_total = 0
position = 1
repeat while n > 0:
    digit = last digit of n
    if position is odd: add digit to odd_total
    otherwise:          add digit to even_total
    remove the last digit from n
    position = position + 1
if odd_total equals even_total: print "balanced"
otherwise: print "not balanced"
```

Notice the pseudocode answers the question "what do I need to remember while I work?" here:
two totals and a position. Deciding *what to remember* is often the main design decision in a
loop problem. These remembered values are called the **state** of the loop.

### Big problems: split into sub-problems

If a problem feels too big, split it into smaller problems you could solve on their own, and
solve them one at a time. "Print a calendar for a month" sounds hard. Split it:

1. Is the year a leap year? (You can solve that.)
2. How many days does this month have? (Uses 1.)
3. On which weekday does the 1st fall? (A formula you can look up and test.)
4. Print the header line.
5. Print the days, starting a new line after each Sunday.

Each sub-problem is a small, testable piece. Write and test them in order. When the last one
works, the whole thing works. You will do exactly this in the "month calendar" challenge.

## Step 5: From pseudocode to code

If the pseudocode is good, this step is almost mechanical: each line becomes one or two lines
of Python. Keep the pseudocode as comments so you can see which part is which.

```python
# Restated: add digits in odd positions (from the right) and in even positions; compare.
n = abs(int(input()))
odd_total = 0
even_total = 0
position = 1
while n > 0:
    digit = n % 10              # last digit
    if position % 2 == 1:
        odd_total += digit
    else:
        even_total += digit
    n //= 10                    # remove last digit
    position += 1
if odd_total == even_total:
    print("balanced")
else:
    print("not balanced")
```

Two habits help a lot here:

- **Write a little, run a little.** Write the input part and print what you read. Run it. Then
  add the loop and print inside it. Run it. You find mistakes when they are one line old, not
  thirty lines old.
- **Do not improve while translating.** If you have a better idea while coding, finish
  translating first, test, and then improve. Changing the plan halfway is how bugs are born.

## Step 6: Dry runs and trace tables

A **dry run** means running the program in your head (or on paper), line by line, exactly as
the computer would, without skipping anything and without assuming. A **trace table** is the
paper you do it on: one column per variable, one row per step (usually per loop iteration).

This is the most important skill in the module. It is how you check code without a computer,
how you find bugs, and how you predict what code does, which is what reading code really means.

Let us trace the balanced-number program for n = 1452. Each row shows the values **at the end
of one loop iteration**.

| iteration | digit | position (before +1) | odd_total | even_total | n after `//= 10` |
|---|---|---|---|---|---|
| start | - | - | 0 | 0 | 1452 |
| 1 | 2 | 1 (odd) | 2 | 0 | 145 |
| 2 | 5 | 2 (even) | 2 | 5 | 14 |
| 3 | 4 | 3 (odd) | 6 | 5 | 1 |
| 4 | 1 | 4 (even) | 6 | 6 | 0 |

Now `n > 0` is false, the loop stops, and 6 == 6, so it prints `balanced`. That matches our
hand answer.

Rules for honest tracing:

1. **Be the computer, not the programmer.** Do what the code says, not what you meant it to
   say. If the code says `<`, do not read it as `<=`.
2. **Write every change.** Do not keep values in your head. The bug is usually in the value you
   did not write down.
3. **Check the loop condition every time**, including the last time when it becomes false.
   Many bugs live in that last check.
4. **Trace the first two iterations and the last one carefully.** The middle usually behaves
   like the first; the ends are where things go wrong.

<details><summary>Try it: trace this program and write exactly what it prints.</summary>

```python
total = 0
i = 1
while i < 10:
    total += i
    i += 3
print(i, total)
```

| iteration | i at start | total after | i after |
|---|---|---|---|
| 1 | 1 | 1 | 4 |
| 2 | 4 | 5 | 7 |
| 3 | 7 | 12 | 10 |

Now `10 < 10` is false and the loop stops. It prints `10 12`. A common wrong answer is `7 12`:
forgetting that `i` was increased once more before the check failed.
</details>

### Tracing nested loops

For nested loops, keep one column for each loop variable and remember: **the inner loop runs
completely for every single value of the outer loop.**

```python
for i in range(1, 4):
    for j in range(i):
        print(i, j)
```

| i | inner range | j values | lines printed |
|---|---|---|---|
| 1 | range(1) | 0 | `1 0` |
| 2 | range(2) | 0, 1 | `2 0`, `2 1` |
| 3 | range(3) | 0, 1, 2 | `3 0`, `3 1`, `3 2` |

Six lines in total: 1 + 2 + 3. When the inner loop depends on the outer variable, the total
work is a sum like this, which is why nested loops get slow quickly.

## Step 7: Edge-case thinking

An **edge case** is an input at the boundary of what is allowed, where a program that works
"normally" might break. Most wrong submissions fail on edge cases, not on normal cases. So
after your program works on the examples, deliberately attack it.

Go through this list every time. For each item, ask: "Is this input allowed by the
constraints? If so, what should the answer be, and what does my program do?"

| Edge case | Why it breaks programs | Typical example |
|---|---|---|
| **Zero** | Loops like `while n > 0` never run; division by zero | digit count of 0 should be 1, not 0 |
| **One** | Special in maths: 1 is not prime, 0! = 1! = 1 | prime check says 1 is prime |
| **Negative** | `%` and `//` behave differently; loops expecting positives stop at once | digit sum of -905 |
| **Largest value** | Too slow, or (in other languages) overflow | n = 10^12 with a loop up to n |
| **Smallest value** | Off-by-one at the start | range starting at 1 versus 0 |
| **Empty input** | Nothing to process: averages divide by zero, "max" has no value | n = 0 numbers |
| **All the same** | "Second largest" has no answer | 5 5 5 |
| **Already the answer** | The loop should run zero times | reversing 7, sorting sorted data |
| **Boundaries of conditions** | `<` versus `<=` matters exactly here | exactly 18 years old, exactly divisible |

Two habits:

- **Decide the correct answer for an edge case before running the program.** If you run first,
  you will be tempted to believe whatever it prints.
- **Read the constraints to know which edges exist.** If `n >= 1` is guaranteed, then n = 0 is
  not an edge case for this problem, and handling it is optional.

<details><summary>Try it: a program reads n numbers and prints their average. List four edge cases and what should happen.</summary>

1. n = 0: there is no average. Dividing by n would crash with `ZeroDivisionError`. The program
   must check for this and print whatever the problem says (for example `no data`).
2. n = 1: the average is that number itself.
3. All negative numbers: the average is negative; make sure nothing assumes positives.
4. Very large numbers: Python integers do not overflow, but if you convert to float you may lose
   precision for numbers above about 10^15.

Others: numbers whose average is not a whole number (do you print `2.5` or `2`?), and the exact
output format (how many decimal places).
</details>

## Off-by-one errors

An **off-by-one error** is a loop that runs one time too many or one time too few, or a count
that is one more or one less than it should be. It is the most common bug in all of
programming, at every level of experience. The cure is not cleverness; it is checking the
boundaries deliberately.

### The fence-post problem

You build a straight fence 10 metres long with a post every metre. How many posts? Not 10.
It is 11: one at 0 m, 1 m, ..., 10 m. The number of **gaps** is 10; the number of **posts**
is 11. Whenever you count things between two endpoints, ask yourself whether you are counting
posts or gaps.

The integers from `a` to `b` **inclusive** number `b - a + 1`. From 3 to 7: 3, 4, 5, 6, 7, that
is five numbers, and 7 - 3 + 1 = 5. Forgetting the `+ 1` is the fence-post mistake.

### `range` is half-open

`range(a, b)` includes `a` and **excludes** `b`. So:

- `range(5)` is 0, 1, 2, 3, 4: five values, and 5 is not one of them.
- `range(1, n)` stops at n - 1. If you want 1 to n inclusive, write `range(1, n + 1)`.
- `range(10, 0, -1)` is 10 down to 1. To include 0, write `range(10, -1, -1)`.

The half-open rule has a good reason: `range(a, b)` has exactly `b - a` values, and
`range(0, n)` matches positions 0 to n-1 in a string of length n.

### `<` versus `<=`

In a `while` loop, the condition decides the last value. Ask: **what is the last value that
should be processed?** Then check that the condition is still true for it, and false for the
next one.

To check divisors up to and including the square root of n, the last d that must be tried is
the one with `d * d == n` (for n = 49, d = 7 must be tried). So the condition is
`d * d <= n`, not `d * d < n`. With `<`, the program would call 49 prime. This exact bug is in
one of this module's problems.

### Where does the counter change?

Look at where the counter is increased relative to where it is used:

```python
i = 0
while i < 3:
    i += 1
    print(i)     # prints 1, 2, 3
```

```python
i = 0
while i < 3:
    print(i)     # prints 0, 1, 2
    i += 1
```

Same condition, different output, because the increase happens before or after the print.

### The three-check method

For any loop, check three things, by hand:

1. **The first iteration.** Are the starting values right? Does the first value processed match
   what you want?
2. **The last iteration.** Is the last value processed the one you want? Trace the loop
   condition with the last value and the value just after it.
3. **The zero case.** If the loop should run zero times (empty input, n = 0), does it? And does
   the program still print the right thing afterwards?

<details><summary>Try it: this code should count the digits of n (n >= 0). Find the bugs.</summary>

```python
n = int(input())
count = 0
while n > 9:
    n //= 10
    count += 1
print(count)
```

Trace n = 7: `7 > 9` is false, the loop does not run, it prints 0. But 7 has one digit. Trace
n = 45: one iteration (45 becomes 4), count 1. But 45 has two digits. The loop stops when one
digit is left, and that digit is never counted. Every answer is one too small: an off-by-one.

Fix: start with `count = 1` (every number has at least one digit, including 0). Then the loop
`while n > 9` removes digits until one remains, counting each removed one. Check: n = 0 gives 1,
n = 7 gives 1, n = 45 gives 2, n = 100 gives 3. All right.
</details>

## Loop invariants, in plain words

A **loop invariant** is a sentence that is true every time the loop is about to check its
condition: before the first iteration, after every iteration, and therefore when the loop
stops. It sounds academic, but it is simply the answer to: **"What do my variables mean right
now?"**

Examples:

- In a sum loop: "`total` is the sum of all numbers read so far."
- In a maximum loop: "`largest` is the largest of the numbers read so far."
- In a digit loop: "`total` is the sum of the digits already removed from `n`."
- In Euclid's gcd loop: "the gcd of `a` and `b` is still the gcd of the two original numbers."

Why does this help? Because if the sentence is true at the start, each iteration keeps it
true, and the loop stops, then the sentence is true at the end. And at the end it usually *is*
the answer. "`largest` is the largest of the numbers read so far", when every number has been
read, means `largest` is the largest number. Done, correct.

Invariants also find bugs at the start. "`largest` is the largest of the numbers read so far."
Before anything is read, what should it be? There is no correct value for "the largest of
nothing", so the clean fix is: read the first number and make it the largest, then loop over
the rest. Starting with `largest = 0` makes the sentence false when all numbers are negative,
and the program prints 0 for the input -5, -2, -9. The invariant tells you why it is wrong.

When you write a loop, say its invariant to yourself in one sentence. If you cannot, you do not
yet know what the loop is doing.

## Debugging by printing state

When a program gives a wrong answer, the worst thing to do is change something and run it
again, hoping. That is not debugging; it is gambling. Real debugging is a search: **find the
first moment where the program's state differs from what you expected.**

The method:

1. Pick a **small** input where the answer is wrong. Smaller is better. Shrink it until it is
   as small as possible while still wrong.
2. Work out by hand what the variables *should* be at each step (a trace table).
3. Add `print` lines inside the loop that show the state:

```python
while n > 0:
    digit = n % 10
    total += digit
    n //= 10
    print("DEBUG digit =", digit, "total =", total, "n =", n)
```

4. Run it and compare line by line with your hand trace. The **first** line that differs tells
   you exactly which step is wrong.
5. Fix that step, run again, and then **remove the debug prints** (checkers will count them as
   wrong output).

Useful details:

- Print labels, not just values. `print(i, j, total)` becomes unreadable after a few lines;
  `print("i =", i, "j =", j, "total =", total)` does not.
- Print just before the loop and just after it too. Many bugs are in the starting values or in
  what happens after the loop ends.
- If a program never finishes, it is stuck in a loop. Print inside the loop and look at the
  variable that should be moving toward the stop condition. It is usually not moving, or moving
  the wrong way. Press `Ctrl+C` to stop the program.
- If Python crashes, read the last line of the traceback first (the error), then the line
  number above it. Go to that line and ask what each value was at that moment.

The same idea works without a computer: a trace table *is* a printed state, written by you.

## A toolkit of loop patterns

Most small logic problems are built from a handful of loop patterns. Experienced programmers
do not invent these each time; they recognise which pattern a problem needs and adapt it. Learn
these until you can write each one without thinking, and say its invariant in one sentence.

### Pattern 1: Digit manipulation

Any non-negative integer can be taken apart from the right with two operators:

- `n % 10` is the last digit. (1234 % 10 is 4.)
- `n // 10` removes the last digit. (1234 // 10 is 123.)

Repeat until `n` becomes 0, and you have visited every digit, right to left.

```python
n = abs(int(input()))      # negative numbers: work with the absolute value
while n > 0:
    digit = n % 10
    # ... use digit ...
    n //= 10
```

Building a number from digits goes the other way: `result = result * 10 + digit` appends
`digit` on the right. Combining the two reverses a number:

```python
n = int(input())           # assume n >= 0 here
reversed_n = 0
while n > 0:
    reversed_n = reversed_n * 10 + n % 10
    n //= 10
print(reversed_n)
```

Trace for n = 120:

| iteration | n % 10 | reversed_n | n after |
|---|---|---|---|
| 1 | 0 | 0 | 12 |
| 2 | 2 | 2 | 1 |
| 3 | 1 | 21 | 0 |

So 120 reversed is 21 (leading zeros vanish in a number). Watch out for two edges: n = 0 makes
the loop run zero times (fine for reversing, wrong for counting digits, since 0 has one digit),
and negative numbers, where `-905 % 10` is 5 in Python and `while n > 0` stops at once. Use
`abs()` and handle the sign separately.

Why use arithmetic instead of converting to a string? Partly because the problems ask you to,
but mostly because digit arithmetic appears everywhere: checksums, base conversion, number
puzzles. And it is the clearest example of a loop that shrinks its input until nothing is left.

### Pattern 2: Counting

Count how many items satisfy a condition. Start at 0; add 1 when the condition holds.

```python
n = int(input())
count = 0
for i in range(n):
    x = int(input())
    if x % 2 == 0:
        count += 1
print(count)
```

Invariant: "`count` is how many of the numbers read so far were even." Before any are read, that
is 0, which is why the count starts at 0.

### Pattern 3: Accumulating

Build up a total (sum, product, combined value) step by step. The starting value is the
"neutral" value for the operation: 0 for a sum (adding 0 changes nothing), 1 for a product
(multiplying by 1 changes nothing).

```python
n = int(input())
factorial = 1
for i in range(2, n + 1):
    factorial *= i
print(factorial)
```

For n = 0 and n = 1 the loop runs zero times and prints 1, which is correct, because 0! = 1.
Starting the product at 0 is a classic bug: everything multiplied by 0 stays 0.

### Pattern 4: Best so far (maximum and minimum)

Keep the best value seen so far, and compare each new item with it.

```python
n = int(input())           # n >= 1
largest = int(input())     # the first number is the best so far
for i in range(n - 1):     # the remaining n - 1 numbers
    x = int(input())
    if x > largest:
        largest = x
print(largest)
```

Starting from the first item (not from 0) keeps the invariant true even for negative numbers.
If you need to know *where* the best was, keep its position in a second variable and update both
together.

A variation, the **second largest**, keeps two variables, `first` and `second`. When a new value
beats `first`, the old `first` moves down to `second`. When it is between them, it replaces only
`second`. Deciding what to do with a value equal to `first` is the edge case that makes this
problem interesting.

### Pattern 5: Searching with a flag

Look for something; stop as soon as it is found. A **flag** is a boolean that records whether it
was found.

```python
n = int(input())
found = False
d = 2
while d * d <= n:
    if n % d == 0:
        found = True
        break
    d += 1
if n >= 2 and not found:
    print("prime")
else:
    print("not prime")
```

Python also has the **loop `else`**: the `else` block of a `for` or `while` runs only if the loop
ended without `break`. It is a built-in flag:

```python
for d in range(2, 10):
    if 91 % d == 0:
        print("found divisor", d)
        break
else:
    print("no divisor below 10")
```

91 = 7 x 13, so this prints `found divisor 7`. If nothing divides, the loop ends normally and
the `else` runs.

The two common flag bugs: forgetting to reset the flag for each new item (when searching inside
an outer loop), and deciding "not found" too early, inside the loop, before all candidates have
been checked.

### Pattern 6: Primes by trial division up to the square root

A number n >= 2 is **prime** if no number from 2 to n - 1 divides it. Checking all of them is
slow for large n. Here is the key insight: if n = a x b, then a and b cannot both be bigger than
the square root of n (their product would be bigger than n). So **if n has any divisor other
than 1 and itself, it has one that is at most the square root of n.** You only need to try d
while `d * d <= n`.

For n = 10^12 this is the difference between a trillion steps (hours) and a million steps
(a fraction of a second).

Why `d * d <= n` instead of `d <= n ** 0.5`? The square root is a float, and floats are
approximations. For large n, `n ** 0.5` can be slightly too small, and you skip the exact root.
`d * d <= n` uses whole numbers only and is always exact.

Trace for n = 49:

| d | d * d <= 49? | 49 % d | result |
|---|---|---|---|
| 2 | 4, yes | 1 | continue |
| 3 | 9, yes | 1 | continue |
| 4 | 16, yes | 1 | continue |
| 5 | 25, yes | 4 | continue |
| 6 | 36, yes | 1 | continue |
| 7 | 49, yes | 0 | divisor found, not prime |

With `d * d < 49`, the loop would stop before d = 7 and wrongly report 49 as prime.

A small speed-up: after checking 2, try only odd d (3, 5, 7, ...). It halves the work.

The same "pair up divisors" idea finds the **sum of all divisors** quickly: each d that divides n
with `d * d <= n` comes with a partner `n // d`. Add both, but when `d * d == n` the partner is d
itself, so add it once.

### Pattern 7: GCD by Euclid's algorithm

The **greatest common divisor** (gcd) of a and b is the largest number dividing both. The slow
way tries every number from min(a, b) down to 1. Euclid's algorithm, over two thousand years
old, is much faster. It rests on one fact:

> gcd(a, b) = gcd(b, a % b), and gcd(a, 0) = a.

Why is the fact true? Write a = q x b + r, where r = a % b. Any number that divides both a and
b also divides a - q x b = r. And any number dividing both b and r also divides q x b + r = a.
So the pairs (a, b) and (b, r) have exactly the same common divisors, and therefore the same
greatest one.

```python
a = abs(int(input()))
b = abs(int(input()))
while b != 0:
    a, b = b, a % b
print(a)
```

Trace for a = 48, b = 18:

| step | a | b | a % b |
|---|---|---|---|
| start | 48 | 18 | 12 |
| 1 | 18 | 12 | 6 |
| 2 | 12 | 6 | 0 |
| 3 | 6 | 0 | - |

b is 0, so the answer is 6. Invariant: "gcd(a, b) equals the gcd of the original numbers." The
loop ends because b gets strictly smaller every step and cannot go below 0.

Note `a, b = b, a % b` computes both right-hand values first, then assigns. Writing `a = b` and
then `b = a % b` on separate lines is wrong, because the second line would use the new a.

The **least common multiple** follows: lcm(a, b) = a // gcd(a, b) x b. Divide first to keep the
numbers small.

### Pattern 8: Number series

A **series** is a sequence where each term comes from the previous ones. The loop keeps just
enough of the past to make the next term.

Factorial keeps one value (`f = f * i`). Fibonacci (0, 1, 1, 2, 3, 5, 8, ...) keeps two, because
each term is the sum of the previous two:

```python
n = int(input())
a, b = 0, 1
for i in range(n):
    print(a)
    a, b = b, a + b
```

Trace for n = 5:

| i | printed | a after | b after |
|---|---|---|---|
| 0 | 0 | 1 | 1 |
| 1 | 1 | 1 | 2 |
| 2 | 1 | 2 | 3 |
| 3 | 2 | 3 | 5 |
| 4 | 3 | 5 | 8 |

Sums of series, like 1 + 1/2 + 1/3 + ... + 1/n, are accumulators: start at 0 and add the next
term each iteration. Alternating series (1 - 2 + 3 - ...) need a sign that flips each step, or
an `if` on whether i is odd or even. And, as we saw, many series have a formula you can find
with a table.

**Simulation** problems are close relatives: a bank balance changing each month, a snail
climbing a well, the Collatz sequence (halve if even, else 3n + 1). The loop applies one step of
the rule per iteration and the state is "where things are now". Simulate first; if the
constraints are too large, look for a formula in the simulated table.

### Pattern 9: Patterns with nested loops

Star and number patterns train exactly the skill of controlling nested loops. Every pattern
problem is solved the same way:

1. Number the rows 1 to n.
2. For row i, write down **how many** of each thing it contains: spaces, stars, numbers.
3. Express those counts as formulas in i and n.
4. Outer loop over rows; inner loop(s) print the parts; then end the line.

A centred pyramid for n = 4:

```text
   *
  ***
 *****
*******
```

| row i | spaces | stars |
|---|---|---|
| 1 | 3 | 1 |
| 2 | 2 | 3 |
| 3 | 1 | 5 |
| 4 | 0 | 7 |

Spaces = n - i. Stars = 2i - 1. Now the code writes itself:

```python
n = int(input())
for i in range(1, n + 1):
    for s in range(n - i):
        print(" ", end="")
    for s in range(2 * i - 1):
        print("*", end="")
    print()
```

`print(..., end="")` prints without moving to a new line; the bare `print()` ends the row.
(You can also write `" " * (n - i) + "*" * (2 * i - 1)`, which builds the row with string
repetition. Both are fine. The nested-loop version is good practice.)

Watch out for **trailing spaces**: a pyramid does not need spaces after the stars, and many
checkers treat them as a different output.

<details><summary>Try it: write the table (row, spaces, stars) for an upside-down pyramid of n = 3 rows, then the formulas.</summary>

```text
*****
 ***
  *
```

| row i | spaces | stars |
|---|---|---|
| 1 | 0 | 5 |
| 2 | 1 | 3 |
| 3 | 2 | 1 |

Spaces = i - 1. Stars = 2(n - i) + 1. Check row 1: 2 x 2 + 1 = 5. Row 3: 2 x 0 + 1 = 1. Right.
</details>

## Worked example 1: Strong numbers

Here is the whole process on a fresh problem, from reading to tested code.

> A number is **strong** if it equals the sum of the factorials of its digits. Read two integers
> lo and hi (1 <= lo <= hi <= 100000). Print every strong number in the range [lo, hi], one per
> line, in increasing order. If there are none, print `none`.

**Step 1, read.** Input: two integers, each on its own line, both at least 1, lo <= hi. Output:
numbers one per line, or the single word `none`. Constraints: hi up to 100,000, so a loop over
the whole range is fine (10^5 numbers, each with at most 6 digits).

**Step 2, restate.** "For each number from lo to hi, add up the factorials of its digits. If the
total equals the number, print it. If I printed nothing, print `none`."

**Step 3, examples by hand.** Try 145: 1! + 4! + 5! = 1 + 24 + 120 = 145. Strong. Try 123:
1 + 2 + 6 = 9. Not strong. Try 1: 1! = 1. Strong. Try 2: 2! = 2. Strong. Try 3: 3! = 6. Not
strong. So for lo = 1, hi = 10 the answer is `1` and `2`. For lo = 3, hi = 100: none of them,
as far as I can tell by checking a few, so `none`. (The full list of strong numbers is
1, 2, 145, 40585, but I would not know that in an exam, and I do not need to.)

**Step 4, plan.** I need three nested ideas: loop over numbers; for each number loop over its
digits; for each digit compute a factorial (another small loop). What do I remember? A flag
`found_any` to know whether to print `none`.

```text
read lo, hi
found_any = False
for x from lo to hi inclusive:
    total = 0
    m = x
    while m > 0:
        d = last digit of m
        f = d!  (multiply 1 x 2 x ... x d)
        total += f
        remove last digit of m
    if total == x: print x, found_any = True
if not found_any: print "none"
```

Check against Step 3: for x = 145 the inner work gives 145, so it prints. For the range 3 to 100
nothing prints and `none` appears. Off-by-one check: "lo to hi inclusive" means `range(lo, hi + 1)`.

**Step 5, code.**

```python
lo = int(input())
hi = int(input())
found_any = False
for x in range(lo, hi + 1):
    total = 0
    m = x
    while m > 0:
        d = m % 10
        f = 1
        for k in range(2, d + 1):
            f *= k
        total += f
        m //= 10
    if total == x:
        print(x)
        found_any = True
if not found_any:
    print("none")
```

Notice `m = x`: the digit loop destroys its number, so it works on a copy. If it changed `x`
directly, the comparison `total == x` would compare with 0. This is one of the most common bugs
in digit problems.

**Step 6, dry run** for x = 145:

| m at start | d | f = d! | total | m after |
|---|---|---|---|---|
| 145 | 5 | 120 | 120 | 14 |
| 14 | 4 | 24 | 144 | 1 |
| 1 | 1 | 1 | 145 | 0 |

total = 145 = x. Printed. Correct.

**Step 7, edge cases.** lo = hi = 1: prints `1`. lo = hi = 3: prints `none`. Digit 0: 0! = 1;
`range(2, 1)` is empty so f stays 1. Correct, and good to have checked, because a number like 40585
contains a 0. Largest range 1 to 100,000: about 500,000 digit steps, each with a tiny inner
loop. Fast enough. Running it prints 1, 2, 145, 40585.

**Complexity.** About (hi - lo + 1) x (number of digits) x 9 steps at most. Fine for these limits.

## Worked example 2: A hollow square

> Read n (1 <= n <= 50). Print an n by n square of `*` whose inside is empty (spaces). No
> trailing spaces.

**Read.** One integer, at least 1. Output n lines.

**Examples by hand.** n = 4:

```text
****
*  *
*  *
****
```

n = 1 is a single `*`. n = 2 is two lines of `**`: no inside at all.

**Plan with a table.** Rows 1 and n are full. Every other row is `*`, then n - 2 spaces, then `*`.

| row | contents |
|---|---|
| 1 | n stars |
| 2 to n-1 | 1 star, n-2 spaces, 1 star |
| n | n stars |

But careful: for n = 1, row 1 and row n are the same row. Print it once. A loop `for row in
range(1, n + 1)` with "if row is 1 or n: full row, else hollow row" handles that automatically,
because there is only one row.

```python
n = int(input())
for row in range(1, n + 1):
    if row == 1 or row == n:
        print("*" * n)
    else:
        print("*" + " " * (n - 2) + "*")
```

**Edge cases.** n = 1: one row, which is row 1, prints `*`. n = 2: rows 1 and 2 are both full,
`**`. Never hollow, correct. n = 3: middle row `* *`. Trailing spaces: none, the last character
of every row is `*`.

<details><summary>Try it: change the plan so the square also has a diagonal from top-left to bottom-right. What is the rule for a single cell?</summary>

Think cell by cell with two nested loops over row r and column c (both 1 to n). A cell is `*` if
it is on the border (r is 1 or n, or c is 1 or n) or on the diagonal (r == c). Otherwise it is
a space.

```python
n = int(input())
for r in range(1, n + 1):
    for c in range(1, n + 1):
        if r == 1 or r == n or c == 1 or c == n or r == c:
            print("*", end="")
        else:
            print(" ", end="")
    print()
```

Thinking cell by cell ("what goes at row r, column c?") is the most general way to solve any
pattern problem.
</details>

## Worked example 3: Let the constraints guide you

> Read n (1 <= n <= 10^10). Print how many numbers from 1 to n have **exactly three** divisors.

**Read.** n can be ten billion. Looping from 1 to n is out of the question (and counting the
divisors of each number would be even worse). The constraint is shouting: there must be a
pattern.

**Examples by hand, as a table.** List the divisors of small numbers and mark those with
exactly three:

| x | divisors | count |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 1, 2 | 2 |
| 3 | 1, 3 | 2 |
| 4 | 1, 2, 4 | **3** |
| 5 | 1, 5 | 2 |
| 6 | 1, 2, 3, 6 | 4 |
| 8 | 1, 2, 4, 8 | 4 |
| 9 | 1, 3, 9 | **3** |
| 12 | 1, 2, 3, 4, 6, 12 | 6 |
| 16 | 1, 2, 4, 8, 16 | 5 |
| 25 | 1, 5, 25 | **3** |

4, 9, 25 ... these are 2 squared, 3 squared, 5 squared: **squares of primes**. 16 = 4 squared
does not count, because 4 is not prime. Why? Divisors come in pairs (d and x // d). To get an
odd count, x must be a perfect square (its root pairs with itself). For exactly three, the only
divisors can be 1, p and p squared, which means p has no divisors except 1 and itself: p is
prime.

**Restate.** "Count the primes p with p x p <= n."

**Plan.** p goes up to the square root of n, at most 10^5. For each candidate p, test primality
by trial division up to its own square root (at most about 316 steps). That is at most a few
million simple steps. Fine.

```python
n = int(input())
count = 0
p = 2
while p * p <= n:
    is_prime = True
    d = 2
    while d * d <= p:
        if p % d == 0:
            is_prime = False
            break
        d += 1
    if is_prime:
        count += 1
    p += 1
print(count)
```

**Test.** n = 1: `2 * 2 <= 1` is false at once, count 0. Correct (1 has one divisor). n = 4:
p = 2 counts, then p = 3 has 9 > 4. Prints 1. Correct. n = 30: p = 2, 3, 5 (25 <= 30), stop at
6 (36 > 30). Prints 3: the numbers 4, 9, 25. Matches the table. Notice `is_prime = True` is
reset **inside** the outer loop, for every p.

The lesson: a big constraint is not a wall. It is a hint that the answer has structure, and
small tables are how you find it.

## Using LeetCode, Codeforces and CSES

This module comes with a list of real problems from three practice sites (`external.toml`; they
appear in your daily plan). Each site has its own style. Here is how to read them.

### How online judges work

An **online judge** runs your program on hidden test inputs and compares its output with the
correct output. On Codeforces and CSES your program is run as a separate process: the judge
**feeds the test data to your program's standard input** (stdin, what `input()` reads) and
**captures its standard output** (what `print()` writes). It is exactly what this module's tests
do to your `solution.py`.

That explains three rules:

- **Never print a prompt.** `input("Enter n: ")` prints `Enter n: ` into the output, and the
  output no longer matches. Always use plain `input()`.
- **Print exactly the required output**, nothing else. No "The answer is". Remove debug prints.
- **Read exactly in the given order.** The input is a stream of lines; each `input()` call takes
  the next line.

Verdicts you will see:

| Verdict | Meaning | What to do |
|---|---|---|
| Accepted | All tests passed | Read others' solutions to learn alternatives |
| Wrong answer on test k | Output differed on test k | Test 1 is usually the sample; later tests are edge cases. Re-read the statement and attack your code with edge cases |
| Time limit exceeded | Too slow | Re-read the constraints; you need a better idea, not tweaks |
| Runtime error | Your program crashed | Usually a wrong input format, a division by zero, or an index problem |

### Reading input on Codeforces and CSES

Problems there often put several numbers **on one line**, separated by spaces, like `3 7`. One
`input()` reads the whole line as text `"3 7"`, and `int("3 7")` fails. You will learn the tools
for this properly later; for now, use these recipes as they are:

```python
# Two (or three) numbers on one line:
a, b = map(int, input().split())

# A count on the first line, then that many numbers on ONE line:
n = int(input())
for x in map(int, input().split()):
    ...                     # x takes each number in turn

# Several test cases: the first line says how many.
t = int(input())
for _ in range(t):
    n = int(input())
    ...                     # solve one case and print its answer
```

`input().split()` cuts the line at spaces into pieces, and `map(int, ...)` turns each piece into
an integer. The "several test cases" format is extremely common on Codeforces: the program
solves many small problems in one run, printing one answer per case.

If a problem has a very large input (hundreds of thousands of lines), plain `input()` can be slow
in Python. Add these two lines at the top and the rest of your code stays the same:

```python
import sys
input = sys.stdin.readline
```

Codeforces lets you choose the language. Choose **PyPy 3** when it is offered: it runs the same
Python code, usually many times faster for loops.

Example: CSES "Weird Algorithm" (task 1068) asks you to print the Collatz-style sequence from n
down to 1, all on one line. A solution using only this module's tools:

```python
n = int(input())
print(n, end=" ")
while n != 1:
    if n % 2 == 0:
        n //= 2
    else:
        n = 3 * n + 1
    print(n, end=" ")
print()
```

(The trailing space at the end of the line is accepted by these judges, which ignore extra spaces
at line ends. This module's tests ignore them too, but problems here will tell you when they
matter.)

### Reading LeetCode problems

LeetCode does not use stdin. It gives you a **function** to complete, inside a `class`:

```python
class Solution:
    def addDigits(self, num: int) -> int:
        ...
```

You have not learned `class` or `def` yet, and you do not need to for these problems. Read it like
this: the input is **already in the variables** named in the brackets (here `num`, an integer).
You write the body, and instead of printing the answer you `return` it. For example:

```python
class Solution:
    def addDigits(self, num: int) -> int:
        while num >= 10:
            total = 0
            while num > 0:
                total += num % 10
                num //= 10
            num = total
        return num
```

The body is the same loop code you write in this module, indented one more level. "Run" tests
your code on the examples; "Submit" runs the hidden tests. LeetCode shows you the failing input on
a wrong answer. Before looking at it, try to guess which edge case it is.

### The three sites, briefly

- **CSES** (cses.fi): a fixed list of about 400 classic problems, grouped by topic. Start with
  "Introductory Problems". Statements are short and precise. Time limits are strict (1 second),
  so a few problems are hard to pass in Python even with the right idea. An account is free.
- **Codeforces** (codeforces.com): thousands of problems from contests, each with a difficulty
  rating. 800 is the easiest. Statements often include a short story; your first job is to strip
  it away and restate the actual task (Step 2). Every problem has an "editorial" (official
  explanation).
- **LeetCode** (leetcode.com): problems grouped Easy, Medium, Hard, with function-style answers.
  Common in job interviews.

### How to practise on them

1. **Time-box.** Give a problem 30 to 45 minutes of real effort using the full process: read,
   restate, examples, plan.
2. **If stuck, take the smallest hint possible.** Read one paragraph of the editorial or
   discussion, then close it and continue on your own.
3. **After solving, compare.** Read one or two other solutions. Was there a simpler idea?
4. **Re-solve later.** A problem you needed help with is not learned until you can solve it cold,
   a week later, from a blank file.
5. **Log it.** Record solves with `learn log cses 1068` (or `learn log codeforces 4A`,
   `learn log leetcode fizz-buzz`), or `learn sync` for Codeforces and LeetCode. Keep your code in
   the folder it shows you.

## The checklist

Copy this somewhere you will see it. Use it for every problem until it becomes automatic.

```text
BEFORE CODING
[ ] Input: what, how many, what order, which lines?
[ ] Output: exact format, words, spacing, decimals, special cases?
[ ] Constraints: smallest and largest values? What do they allow?
[ ] Speed: how many steps will my idea take at the largest input?
[ ] Restate the problem in one or two sentences (as a comment)
[ ] Solve the given examples by hand. Do my answers match?
[ ] Solve 2-3 examples of my own, including an edge case
[ ] Watch what I did by hand: that is the algorithm
[ ] Pseudocode: steps, what I remember (state), what I print
[ ] Say the loop's invariant in one sentence

WHILE CODING
[ ] Translate the pseudocode line by line
[ ] Write a little, run a little
[ ] No prompts in input(); no extra output

AFTER CODING
[ ] Dry run one small example with a trace table
[ ] Check first iteration, last iteration, zero iterations
[ ] Edge cases: 0, 1, negative, largest, empty, all equal, boundaries
[ ] Wrong? Shrink the input, print state, find the FIRST difference
[ ] Remove debug prints
```

## Summary

- Solving a problem is a process, not inspiration: read, restate, work examples by hand, plan in
  pseudocode, translate, dry run, attack with edge cases, debug by printing state.
- The input, output and constraints together define the problem. Constraints tell you which edge
  cases exist and how fast the solution must be. Ten million simple steps per second is a useful
  estimate for Python.
- If you cannot solve an example by hand, you cannot program it. Tables of small cases reveal
  patterns and formulas.
- Pseudocode is plain-language steps that name the loop's state: what it must remember.
- A trace table is the honest record of what code does, one column per variable, one row per
  step. It is how you read, check and debug code without a computer.
- Edge cases (zero, one, negative, largest, empty, all equal, boundaries) cause most wrong
  answers. Decide their correct answers before running the code.
- Off-by-one errors live at loop boundaries: `range` excludes its end, `b - a + 1` counts an
  inclusive range, and `<` versus `<=` decides the last value. Check the first, last and zero
  iterations.
- A loop invariant is a sentence about what the variables mean, true before and after every
  iteration. When the loop ends, it usually states the answer.
- The core patterns: digits with `% 10` and `// 10`, counting, accumulating, best so far,
  searching with a flag or loop `else`, trial division up to the square root, Euclid's gcd,
  series and simulations, and patterns built from per-row formulas.
- Online judges feed your program stdin and compare stdout, which is why prompts and extra output
  are wrong.

## Learning outcomes checklist

Tick these honestly. Each one should be true without looking anything up.

- [ ] Given a short problem, I can name its input format, output format and constraints, and say
  what the constraints imply about speed and edge cases.
- [ ] I write a restatement and a plan (pseudocode) **before** writing code, every time.
- [ ] I can trace a loop, including nested loops, with a trace table and predict its exact output.
- [ ] I can find an off-by-one bug by checking the first, last and zero iterations.
- [ ] I can state the invariant of a counting, accumulating or best-so-far loop.
- [ ] I can list the edge cases of a problem and their correct answers before running anything.
- [ ] I can debug a wrong answer by shrinking the input and printing state.
- [ ] I can write from memory: digit extraction, reversing a number, counting, max/min without
  storing the numbers, a prime check up to the square root, Euclid's gcd, Fibonacci and factorial
  loops, and a centred pyramid.
- [ ] I can read a Codeforces or CSES input format and a LeetCode function signature.

## Further reading

- Python tutorial, "More Control Flow Tools" (loops, `range`, `break`, loop `else`):
  https://docs.python.org/3/tutorial/controlflow.html
- The `range` type and its exact rules: https://docs.python.org/3/library/stdtypes.html#range
- Python Tutor, which draws your program's state step by step (a trace table made for you; use it
  to check your hand traces, not to replace them): https://pythontutor.com/
- CSES Problem Set (start with Introductory Problems): https://cses.fi/problemset/
- "Competitive Programmer's Handbook" by Antti Laaksonen, free from the CSES site, chapters 1 and 2
  on how problems and time limits work: https://cses.fi/book/book.pdf
- Codeforces problem set (sort by difficulty, start at 800): https://codeforces.com/problemset
- LeetCode problem list (filter by Easy): https://leetcode.com/problemset/
- George Polya, *How to Solve It* (1945). A short, classic book about exactly this chapter's
  subject: understanding the problem, making a plan, carrying it out, and looking back. It is about
  mathematics, but every idea applies to programming.
