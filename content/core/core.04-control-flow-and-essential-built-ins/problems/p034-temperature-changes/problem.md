# Day-to-day temperature changes

Read one line of daily temperatures (whole numbers, separated by spaces). Day 1 is the first.

For each day from day 2 on, print the change from the day before:

```
Day 2: +2
Day 3: -1
Day 4: 0
```

A rise has a `+` sign, a fall a `-` sign, and no change is just `0`.

Then print the biggest rise as `Biggest rise: +N on day D`. If several days tie, report
the **earliest**. If the temperature never rises, print `No rises`.

If there are fewer than 2 temperatures, print only `Not enough data`.

**Example**

Input `30 32 31 31 35`. Output:

```
Day 2: +2
Day 3: -1
Day 4: 0
Day 5: +4
Biggest rise: +4 on day 5
```
