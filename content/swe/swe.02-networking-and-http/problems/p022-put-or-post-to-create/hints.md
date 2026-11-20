## Hint 1

In design 2 the URL already contains the id. Who wrote it? In design 1 the client does not send an id. Who makes one?

## Hint 2

Think of the lost reply: from the client's point of view the first request "failed". What did the server actually do? Run the repeated request through each design.

## Hint 3

An idempotency key is a unique token the client generates **once** for the operation and sends with every retry. The server saves "key → result" and, when it sees the key again, returns the saved result instead of working again.
