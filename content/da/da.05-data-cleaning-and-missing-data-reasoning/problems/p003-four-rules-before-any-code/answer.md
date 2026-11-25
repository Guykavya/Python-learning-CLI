## Model answer

1. **Rules broken.**
   - **Never edit the raw data.** The teammate saved over the file, so the original is gone. If a mistake is found
     later there is nothing to go back to.
   - **Every change must be countable.** "Not many" is not a number. Nobody can say how many rows or which ones were
     removed, so the effect on the averages cannot be reported or checked.
   - **Flag before you delete.** Rows were deleted because they "looked wrong". A flag column would have cost
     nothing and could be undone; a deletion cannot. Retyping ages by hand also invents values without a rule anyone can
     read.
   - Fixing by hand in the file itself also means the cleaning cannot be repeated by a script.

2. **What to do instead.** Keep the raw file untouched. Write a **script** that reads the raw file and writes a new clean
   file: each rule is a line of code (a range rule for age, a mapping for city spellings, a drop of exact duplicates),
   and every step is written to a **change log** with rows before and after and a short reason. When the owner sends a
   corrected export, run the script again and compare the new log with the old one.

3. **Plausible is not correct.** A script can run cleanly and still be wrong (a date parsed with day and month swapped
   raises no error). Always **check against something known**: a column you trust, the number of respondents the survey
   office reports, a small hand-checked sample, or, when you can build it, a clean "truth" copy (as the chapter does) so
   the cleaned result can be compared with it. Put the check in the script as an `assert` so a surprise stops the run
   instead of slipping through.

**Checklist: your answer should mention**
- [ ] never edit or overwrite the raw data (keep the original)
- [ ] every change must be countable (a change log with numbers)
- [ ] flag before you delete (a deletion cannot be undone)
- [ ] cleaning is a script, never fixes by hand in the file (reproducible)
- [ ] check the result against something known (a total, a trusted column, a truth)
