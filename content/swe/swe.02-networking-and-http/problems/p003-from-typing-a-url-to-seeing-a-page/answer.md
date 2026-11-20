## Model answer

1. **Parse the URL** (browser). Scheme `https` (so port 443), host `shop.example`, path `/books`, query `page=2`, fragment `top`. *Can fail:* a malformed URL; the browser searches the web instead.
2. **DNS** (application protocol, usually over UDP). The name `shop.example` is looked up (browser cache, operating system, the resolver of the network) and an IP address comes back. *Can fail:* the name does not exist or the resolver is down: "server not found".
3. **TCP handshake** (transport layer). The client sends SYN, the server answers SYN-ACK, the client ACKs: a reliable byte stream to `IP:443` exists. *Can fail:* nothing listens (connection refused), a firewall drops packets (timeout).
4. **TLS handshake** (on top of TCP). The client says which host it wants (SNI) and which versions it speaks; the server sends its certificate; the client checks that a trusted authority signed it, that it is for `shop.example` and not expired; both sides agree on keys. *Can fail:* expired or wrong-name certificate: a security warning page.
5. **HTTP request** (application layer, now encrypted). `GET /books?page=2 HTTP/1.1` with `Host: shop.example` and headers such as `Accept`, cookies. The fragment is **not** sent.
6. **HTTP response.** A status line (`200 OK`), headers (`Content-Type`, `Content-Length`, maybe `Set-Cookie`) and the body (HTML). *Can fail:* `404`, `500`, a timeout while waiting.
7. **Keep-alive.** The browser keeps the connection open for the next requests (images, CSS, JavaScript), to avoid paying for DNS, TCP and TLS again; HTTP/2 even mixes many requests on one connection.
8. **The browser works on the page.** It parses the HTML, finds more resources, fetches them (steps 5 to 7 again, possibly to other hosts), builds the layout and draws it. Scripts may make more requests.
9. **The fragment** `#top` is used only by the browser: after the page loads it scrolls to the element with `id="top"`. The server never sees it.
10. **Close or keep.** After idle time or when the tab closes, the connection is closed (FIN) or the server drops it.

**What an eavesdropper still sees with HTTPS:** the IP address of the server, the host name (in the DNS lookup, unless encrypted, and in the SNI of the TLS handshake), the size and timing of the traffic. The path, query string, headers, cookies and body are hidden.

**Checklist: your answer should mention**
- [ ] URL parts: scheme, host, port 443, path, query, **fragment**
- [ ] **DNS** turns the name into an IP address
- [ ] **TCP handshake** (SYN, SYN-ACK, ACK) gives a reliable stream
- [ ] **TLS handshake** and **certificate check** (trusted, right name, valid dates)
- [ ] the **HTTP request** (method, path, `Host` header) and **response** (status, headers, body)
- [ ] **keep-alive** reuses the connection
- [ ] the browser parses HTML and fetches more resources
- [ ] the **fragment is never sent** to the server
- [ ] at least **three different failures** at different layers
- [ ] what stays visible: IP, host name (SNI), sizes and timing
