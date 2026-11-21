## Hint 1

Ask two questions for each situation. (a) Did Nginx get **any** answer from a backend? If a connection is refused immediately, or the answer is garbage, the verdict is 502. If it waits and gives up, the verdict is 504. (b) Is there another backend to try for a `GET`?

## Hint 2

Situation 2 is the chapter's "surprise": an address nobody answers on does not fail at once, it times out. Situation 6: the crashed backend refuses (502 for that attempt), Nginx moves on to the healthy one, and the client only sees what the last attempt gave.
