# Pick the right method

For each task below, name the string tool you would use and explain in one or two sentences **why**, including what could go wrong with the obvious alternative. Write your answer in `answer.md`.

1. A log line is read. You want to know whether the word `ERROR` appears anywhere in it.
2. A settings line looks like `key=value`, but the value itself may contain `=`. You want the key and the value.
3. A data file must contain the marker `###` on each line. You need its position, and a missing marker is a bug in the file that should stop the program loudly.
4. File names end in `.csv`. You want the name without that ending. (Someone suggests `name.rstrip(".csv")`.)
5. You compare a typed username with a stored one, ignoring case, for users from many countries.

Example of the expected style, for a different task: *"To get the last three characters I would use `s[-3:]`, because slicing never fails, so a two-character string gives back both characters instead of crashing like an index would."*
