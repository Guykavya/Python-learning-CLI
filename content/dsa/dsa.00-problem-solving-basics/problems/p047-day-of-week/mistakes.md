- Forgetting the 100/400 rule: treating 1900 as a leap year makes 29 2 1900 look valid.
- Not moving January and February to months 13 and 14 of the previous year. Every date in those
  two months then comes out on the wrong weekday, while March to December look fine.
- Using `/` instead of `//` in the formula. The result becomes a float and `% 7` no longer gives
  a clean 0..6, so no `if h == ...` branch matches correctly.
- Checking only `day <= 31` instead of the real length of the month, so 31 4 2024 is accepted.
