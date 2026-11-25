# Four rules before any code

Chapter section 1. A teammate sends you this message:

> "The survey file had some junk, so I opened it in Excel, deleted the rows that looked wrong, retyped a few ages by
> hand, saved over the file and ran my averages. They look fine! I can't remember exactly which rows I removed, but it
> was not many."

Explain in `answer.md`, in about 150 to 250 words:

1. Which of the chapter's cleaning rules does this break? Name at least **three** and say what goes wrong for each.
2. Describe what the teammate should do instead, step by step, so that the result can be reproduced next week when the
   raw file is corrected.
3. A cleaning script runs without errors and prints plausible numbers. Why is that **not** proof that the cleaning is
   right, and what can you compare the result with?

## Example

A start: "Saving over the file destroys the raw data (rule 1). If the owner sends a corrected export, nothing can be
re-run, because the cleaning lived in someone's mouse clicks..."
