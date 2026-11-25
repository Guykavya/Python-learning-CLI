- **`pd.to_datetime(s, dayfirst=True, format="mixed")` for everything.** It reads the ISO date `2024-03-05` as 3 May
  (year, *day*, month) and raises no error. Choose the format from the pattern.
- **`dayfirst=False` for everything.** Then `05/03/2024` becomes 3 May. Ambiguous slash dates are day first here.
- **Parsing without checking the pattern first.** `strptime` with `%d/%m/%Y` happily accepts `5/3/24`-like variants in
  some versions or fails with a message that hides which text was wrong. A full-match pattern makes the contract exact.
- **Using `match` instead of `fullmatch`.** `"2024-03-05 extra"` starts like a date; only a full match says "this whole
  text is one date".
- **Letting `31/04/2024` raise.** An impossible date is data, not a crash: `NaT`, and listed in `bad`.
- **Listing the original text with its spaces** in `bad`, or listing missing inputs. Strip first; missing is not "bad".
