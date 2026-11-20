## Approach

The model answer is in `answer.md`. A short rule to remember: **TLS protects the content in transit between two verified ends; it does not hide who talks to whom, how much, and when; and it is only as good as the check of who the other end is.**

You can see the metadata yourself: in a packet capture of an HTTPS visit, the host name appears in plain text in the first handshake message (SNI).

## Complexity

Not applicable.

## Another way

For private browsing of the *destination*, tools such as a VPN, encrypted DNS, or Encrypted Client Hello hide more, but each moves the trust somewhere else.

## Why it matters

Knowing exactly what HTTPS gives you stops two opposite mistakes: thinking it hides everything, and turning verification off "just to make it work".
