- **Reading `"."` as a dot in the regex call.** In a pattern it is any character; line 2 empties every string.
- **Reading `"1+1"` as the text "1+1" in the regex call.** There it means "at least two 1s in a row"; `211` matches and
  the string `1+1` does not.
- **Thinking `regex=False` and `regex=True` differ only in speed.** They give different answers.
- **Counting the characters instead of the digits on line 5.** `\d` matches digits only.
- **Writing `False`/`True` as strings, or forgetting the brackets** of `.tolist()` output.
- **Writing `0` or `1` for line 7.** It is two numbers separated by a space: `4 1`.
