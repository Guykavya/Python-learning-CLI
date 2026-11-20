## Approach

The naive loop just prints the chunks. The framed loop, step by step:

| After chunk | `buf` | What happens |
|---|---|---|
| 1 `\x05HEL` | `\x05HEL` | needs 6 bytes, has 4: wait |
| 2 `LO\x07WORLD!` | `\x05HELLO\x07WORLD!` | `HELLO` is complete: print; then `\x07WORLD!` needs 8, has 7: wait |
| 3 `!\x03BY` | `\x07WORLD!!\x03BY` | `WORLD!!` complete: print; `\x03BY` needs 4, has 3: wait |
| 4 `E` | `\x03BYE` | `BYE` complete: print; `buf` is empty |

Output (checked by running the code):

```text
naive: b'\x05HEL'
naive: b'LO\x07WORLD!'
naive: b'!\x03BY'
naive: b'E'
framed: b'HELLO'
framed: b'WORLD!!'
framed: b'BYE'
left over: b''
```

None of the naive lines is a whole message: three messages became four chunks, and the cut points are in the middle of messages, even inside one of them. The framed receiver gets all three, because the length byte tells it where each message ends and the leftover waits in `buf`. A non-empty `left over` would mean the connection ended in the middle of a message.

## Complexity

Not applicable.

## Another way

Make the pieces differently (one byte at a time, or everything in one chunk) and check that the framed output does not change. That independence from the cut points is the whole purpose of framing.

## Why it matters

On a fast loopback connection "one recv = one message" often works in tests, and breaks the day packets are cut by a real network. Framing makes the behaviour independent of how TCP cuts the stream.
