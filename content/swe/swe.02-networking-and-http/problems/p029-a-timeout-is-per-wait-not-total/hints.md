## Hint 1

Check the gaps between bytes, not the total time: byte 1 arrives at 0.8 s, byte 2 at 1.6 s, so each wait is 0.8 s. Compare 0.8 with each timeout.

## Hint 2

For the 0.5-second timeout the very first wait (0.8 s) is longer than 0.5 s: the client gives up at `0 + 0.5 = 0.5` seconds with 0 bytes received.

## Hint 3

For the deadline of 3.0 s: bytes arrive at 0.8, 1.6, 2.4. After byte 3 (`clock = 2.4`) only 0.6 s remain, so `wait = min(1.0, 0.6) = 0.6`; the next byte needs 0.8 s: timeout at `2.4 + 0.6 = 3.0` seconds with 3 bytes.
