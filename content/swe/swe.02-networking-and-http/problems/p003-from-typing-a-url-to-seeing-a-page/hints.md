## Hint 1

Start with the URL itself: which piece names the protocol, which the machine, which the resource on it? Then ask: how does a *name* become something a network can deliver to?

## Hint 2

The order of the layers is the order of the journey: name to address (DNS), address to a live connection (TCP handshake), then a secure channel on top of it (TLS handshake, certificate check), then the HTTP request and response.

## Hint 3

For failures: DNS gives "server not found"; TCP gives "connection refused" or a timeout; TLS gives a certificate warning; HTTP gives a status such as 404 or 500. The fragment `#top` never leaves the browser (section 13.3).
