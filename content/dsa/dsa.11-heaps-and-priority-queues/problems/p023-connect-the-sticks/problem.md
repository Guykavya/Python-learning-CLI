# Connect the sticks

You have sticks with the lengths in the list `sticks`. Joining two sticks of lengths `a` and `b` costs `a + b` and gives one new stick of length `a + b`. Join all sticks into **one** stick. Write `connect_sticks(sticks)`, which returns the **smallest possible total cost**.

A single stick (or no stick) needs no joining: the cost is `0`. Do not change the input list.

## Example

```python
>>> connect_sticks([2, 4, 3])
14
>>> connect_sticks([1, 8, 3, 5])
30
>>> connect_sticks([5])
0
>>> connect_sticks([])
0
```

For `[2, 4, 3]`: join `2` and `3` (cost 5, new stick 5), then `5` and `4` (cost 9): total `5 + 9 = 14`. Joining `4` and `3` first would cost `7 + 9 = 16`.

## Constraints

- Up to 100,000 sticks, each length a positive integer.
- The big test (65,536 sticks of length 1) runs in a separate process with a 10-second limit.

## Think about

A stick that is joined early is part of every later stick that contains it, so its length is paid again and again. Which two sticks should you join first, if you want long sticks to be paid as few times as possible? Which data structure gives you the two smallest items again and again?
