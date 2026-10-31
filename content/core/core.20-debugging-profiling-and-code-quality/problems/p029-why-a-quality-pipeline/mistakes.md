- **Claiming mypy catches the division by zero.** The types are fine; the value is the problem.
  Static tools do not know which values arrive.
- **Saying the formatter "fixes bugs".** It changes only layout. That is still valuable
  (readable diffs, no style arguments), but it is not checking.
- **Missing the money problem on line 5.** It is the real bug there; the spacing is cosmetic.
- **Saying "tests are enough" or "types are enough".** Each layer has blind spots the others
  cover; say which.
- **Putting the slow test suite in a pre-commit hook without saying the cost.** Slow hooks
  teach people to skip them with `--no-verify`.
- **Forgetting that fixers change files.** That is the reason they run first.
- **No answer to the teammate.** The last question asks for a short, direct reply.
