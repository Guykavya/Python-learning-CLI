- Buying at the overall lowest price and selling at the highest price after it. For `3 8 1 5` that
  gives profit 4 (buy day 3, sell day 4), but buying on day 1 and selling on day 2 gives 5.
- Trying every pair of days with two nested loops. It gives the right answer, but for 100000 days
  that is about 5 billion pairs and the program runs for hours.
- Using `>=` for the best profit or `<=` for the minimum. Both silently break the tie rules: the
  program reports a later sell day or a later buy day.
- Printing `buy 0 sell 0` when there is no profit. The statement asks for only `profit 0`.
