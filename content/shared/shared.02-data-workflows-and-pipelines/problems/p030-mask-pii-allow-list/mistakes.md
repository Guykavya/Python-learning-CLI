- Using a deny-list (`if key != "email"`). It works today and leaks tomorrow, when the source adds
  `phone` or `address`. Always build the output from the allow-list.
- One star per hidden letter (`a***` for `asha`, `a*********` for `alexandra`). The length is a
  strong clue for guessing the name. Use a fixed `***`.
- Splitting at the first `@` with `split("@")[1]`. It crashes on `"broken"` (IndexError) and gives
  the wrong domain when the local part contains `@`.
- Returning the malformed value unchanged. A wrong value in an email box is often other personal
  data (a phone number, a full name). Mask it completely.
- Turning `None` into `"***"`. "No email" and "hidden email" are different facts.
- Deleting keys from the input dicts. Other steps of the pipeline still need the original row.
- Forgetting to strip and lower-case first, so `" Asha@Example.com"` is masked as `" ***@Example.com"`
  and the same customer looks different in two exports.
