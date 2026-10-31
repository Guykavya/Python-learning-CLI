# Explain: why store times in UTC?

A common rule in backend code is: **"Store and compute in UTC. Convert to local time only at the
edges (when reading input and when showing output)."** A teammate disagrees. Their app is used
only in London, so they store local wall-clock times as naive strings, like `"2024-10-27 01:30"`,
in a SQLite table of door-entry events.

In `answer.md` (about 250 to 400 words), explain:

1. What exactly goes wrong with the teammate's table on the night of 27 October 2024 (London's
   clocks go back from 02:00 BST to 01:00 GMT), and on 31 March 2024 (01:00 GMT to 02:00 BST)?
   Give one concrete query or calculation that gives a wrong answer.
2. Why does a naive `datetime` make this worse in Python? (What does `.astimezone()` do with one?
   What happens when you compare naive and aware values?)
3. What "convert at the edges" means in practice: where the conversion to UTC happens, what is
   stored (and in what format), and where the conversion back to local time happens.
4. One case where storing UTC alone is **not** enough, and what you would store instead.
   (Think about a dentist appointment at 09:00 local time next year, when a government may change
   the DST rules before then.)

**Example** of the level of detail wanted, for a different question: *"Sorting the strings
`'2024-10-27 01:45'` (BST) and `'2024-10-27 01:15'` (GMT) puts the GMT event first, although it
happened 30 minutes later."*
