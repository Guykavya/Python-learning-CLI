## Hint 1

TLS protects the **content** of the conversation between the two ends. Think of an envelope: what is written inside versus what is written on the outside so that the post can deliver it.

## Hint 2

The network must still know where to send the packets (the IP address), and the server's name is sent at the start of the handshake so that the right certificate can be chosen. What does the observer learn from the size and timing of the packets?

## Hint 3

A certificate says "this public key belongs to this name, and an authority you trust signed it". Does it say the owner is honest? And what does a client that skips the check lose: it can no longer tell the real server from a man in the middle.
