# Read the constraints first

Each task below has a time limit of **1 second**, and you will solve it in Python. Use the rule of thumb from the
chapter: Python does roughly **10^7 simple operations per second** (C++ does about 10^8).

For each task, in `answer.md`:

- estimate how many operations the given idea needs at the **largest** input, and say whether it will pass;
- say which complexity class you need (the slowest one that still fits), and name an approach if you can.

**A.** Given `n <= 20` items with weights, decide whether some group of them weighs exactly `W`. Idea: try all
groups (every subset).

**B.** Given `n <= 2000` points, find the two closest ones. Idea: check every pair.

**C.** Given `n <= 200000` numbers, find the two closest **values**. Idea: check every pair.

**D.** Given one number `n <= 10^12`, decide whether it is prime. Idea: try every divisor from 2 to `n - 1`.

**E.** Given `n <= 10^5` numbers and `q <= 10^5` questions "how many numbers are smaller than x?". Idea: for each
question, loop over all numbers.

**F.** Given `n <= 10` cities, find the shortest route that visits all of them. Idea: try every order of cities.

**G.** Given `n <= 10^18`, print the sum `1 + 2 + ... + n`. Idea: loop from 1 to `n`.

Finish with one paragraph: what is the first thing you do when you open a new problem, and why?
