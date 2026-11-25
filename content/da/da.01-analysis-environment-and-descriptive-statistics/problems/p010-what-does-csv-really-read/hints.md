## Hint 1

For each line ask three things: where are the commas that really split fields (outside quotes)? Is there any quote character left in the result? What does the empty line produce: nothing, or an empty list?

## Hint 2

`csv` never strips spaces: `"Chen "` and `" 70"` keep them. The two quote rules are: a quoted field loses its outer quotes, and `""` inside it becomes a single `"`. Python then prints a string containing a double quote with single outer quotes.
