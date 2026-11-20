# Explain: which tool for which string problem?

Chapter section 16 has a decision guide. Use these labels:

| Label | Tool |
|---|---|
| `BUILTIN` | `in`, `str.find`, `str.startswith` and friends |
| `TRIE` | a trie (or a sorted list with `bisect`) |
| `KMP` | prefix function / KMP |
| `Z` | Z-function |
| `RK` | Rabin-Karp, rolling or prefix hashes |
| `MANACHER` | Manacher's algorithm |

For each task, choose the **best** label: correct, fast enough for the sizes given, and as simple as possible.

1. A phone shows contact names that start with the letters typed so far; 50,000 contacts, a new query on every key press.
2. Does a 2 MB log file contain the text `ERROR 503`? Asked once.
3. Network bytes arrive one at a time. Raise an alarm the moment a fixed 40-byte signature has appeared, without storing the stream.
4. Is a 10**6-letter string made of one shorter block repeated several times?
5. Find every position in a book where any of 500 banned words of exactly 8 letters occurs.
6. The longest palindromic substring of a DNA string of 10**6 letters.
7. For every position of a 10**6-letter DNA read, how many leading letters of a 1000-letter reference sequence match there.
8. The longest passage that occurs twice in a 10**5-character document.

Write your answer in `answer.md`: one line per task with the label and a reason of 5 to 15 words. Then, for **two** tasks of your choice, explain in 3 to 4 sentences why a tempting other tool is worse (for example `BUILTIN` for task 5, or `KMP` for task 7).

Then compare with the model answer and rate yourself.
