# Explain which pattern fits

Real problems do not say "use a sliding window". You have to recognise the shape. For each scenario below, write in
`answer.md`:

- the **pattern** you would use (prefix sums, difference array, two pointers, fixed window, variable window, Kadane,
  prefix sums with a dictionary, monotonic deque, or a matrix walk);
- **why** it fits: which property of the input makes it work (sorted? all positive? fixed size? many queries?);
- the **time** it takes, against the obvious brute force;
- one **trap**: a small change to the scenario that would break your choice.

Aim for 60 to 100 words per scenario.

1. A shop logs its profit or loss for each of 365 days (negative on bad days). The owner asks: "What was the best run
   of consecutive days, by total profit?"
2. A delivery app stores 200000 order amounts in a list. Ten thousand times a day, an analyst asks: "What is the total
   of orders number `l` to `r`?"
3. A school has a **sorted** list of student heights and wants to know whether two students' heights add up to exactly
   `H`.
4. A sensor sends one positive reading per second. Find the shortest stretch of seconds whose readings add up to at
   least `S`.
5. A stadium has 100000 seats in a row. 50000 ticket groups each book "seats `l` to `r`, add `v` people" (allowed to
   overlap). After all bookings, print how many people sit in each seat.

Then read `solution.md` and `answer.md`, and rate your answer.
