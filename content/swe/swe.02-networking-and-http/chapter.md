# Chapter 2 (SWE): Networking and HTTP

Almost every program you will write at work talks to another computer. A mobile app asks a server for your orders. A web page asks an API for prices. Your own service asks a payment provider to charge a card. A scraper asks a website for its pages. In all of these, bytes leave one machine, cross a network that can be slow, broken or hostile, and arrive at another machine that may be busy, down or buggy.

This chapter teaches how that works, from the bottom (addresses and sockets) to the top (REST APIs and resilient clients). It builds on **swe.01** (project habits) and on **core.17** (`urllib`, `json`, `logging`) and **core.21** (threads, `httpx`, `MockTransport`). You do not need to re-learn those; we use them.

By the end you reach two outcomes:

- You can **explain what happens between typing a URL and seeing a page**, step by step, and say which step is slow or can fail.
- You can **call an API with timeouts and safe retries**: you know which requests may be repeated, how long to wait, and how to give up.

And the project at the end has two parts: a **raw-socket HTTP server** you write yourself, and a **resilient API client** you test against a server that fails on purpose.

Along the way you will answer these questions:

- What are the layers of a network, and what does each one promise?
- What is an IP address, a port, `localhost`, and what is DNS for?
- What is the difference between TCP and UDP? What is a "byte stream", and why does one `send` not equal one `recv`?
- What does an HTTP request really look like on the wire? (It is just text.)
- What do `GET`, `POST`, `PUT`, `DELETE` mean? What is "safe" and what is "idempotent"?
- Which status codes must you know, and what do headers like `Content-Type`, `ETag`, `Authorization` do?
- What is a cookie? What is a session?
- What is HTTPS? What does a certificate prove?
- What are REST and JSON APIs? How do pagination and errors look?
- How do `requests` and `httpx` differ? Why does `requests.get(url)` with no timeout wait forever?
- How do you retry with exponential backoff and jitter? Which requests are dangerous to retry?
- How do you read data out of an HTML page with BeautifulSoup, politely?

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux, `requests 2.34`, `httpx 0.28`, `beautifulsoup4 4.15` and OpenSSL 3.5. The output you see is the real output. Some values change from machine to machine; where that matters the text says so. These are always **machine-specific**: ports chosen by the operating system, timings, dates, process ids, certificate fingerprints, and anything that comes from the real internet. Never copy such a value from this book; read the *shape*.

**Offline by design.** Everything you must *run* works with **no internet**. The trick is the loopback address `127.0.0.1`, which always means "this computer". We start small servers **inside** the example code (in a background thread) and talk to them from the same program. Things that need the real internet (a real DNS lookup, a real HTTPS site, `curl` against a public API) are placed in clearly marked **"Try it on your machine"** boxes. In those boxes the command is exact and the output is *described* (or shown with invented values that are clearly labelled), because it was not captured here.

**Ports and your firewall.** Read this once. A *port* is a number that says which program on a computer should get a connection. Our servers always use **port 0**, which means "operating system, please choose any free port for me". We then read back which one was chosen. We never hard-code a number like 8000, so two exercises can never fight over the same port, and a leftover program from yesterday cannot break today's example. All servers bind to **`127.0.0.1` only**. That address is not reachable from other computers, so the examples are private and a firewall has nothing to block. If a firewall or security tool on your machine does ask "allow this program to accept incoming connections?", you can safely answer **no**: loopback traffic never leaves your computer. (If you ever bind to `0.0.0.0`, the server is visible to your whole network, and the firewall prompt is real and important. We will not do that here.)

**Check your tools first.**

```python
import sys, socket, ssl
import requests, httpx, bs4

print("python", sys.version.split()[0])
print("requests", requests.__version__, "| httpx", httpx.__version__, "| bs4", bs4.__version__)
print("openssl", ssl.OPENSSL_VERSION.split()[1])
print("loopback works:", socket.getaddrinfo("127.0.0.1", 80, type=socket.SOCK_STREAM)[0][4])
```
```text
python 3.14.4
requests 2.34.2 | httpx 0.28.1 | bs4 4.15.0
openssl 3.5.5
loopback works: ('127.0.0.1', 80)
```

Your versions may be a little different. That is fine. If `import requests` or `import httpx` fails, install them into your virtual environment with `python -m pip install requests httpx beautifulsoup4` (this needs the internet once; the course environment already has them).

## Table of contents

1. [Why networks are hard](#1-why-networks-are-hard)
2. [The layers model](#2-the-layers-model)
3. [IP addresses, ports and localhost](#3-ip-addresses-ports-and-localhost)
4. [DNS: names to addresses](#4-dns-names-to-addresses)
5. [Sockets: TCP and UDP on loopback](#5-sockets-tcp-and-udp-on-loopback)
6. [The byte-stream problem: framing](#6-the-byte-stream-problem-framing)
7. [HTTP is text on a TCP stream](#7-http-is-text-on-a-tcp-stream)
8. [Anatomy of a request and a response](#8-anatomy-of-a-request-and-a-response)
9. [Methods: safe and idempotent](#9-methods-safe-and-idempotent)
10. [Status codes](#10-status-codes)
11. [Headers that matter](#11-headers-that-matter)
12. [Cookies and sessions](#12-cookies-and-sessions)
13. [URLs and `urllib.parse`](#13-urls-and-urllibparse)
14. [JSON APIs and REST](#14-json-apis-and-rest)
15. [Building an HTTP server from raw sockets](#15-building-an-http-server-from-raw-sockets)
16. [`http.server` and Flask, compared](#16-httpserver-and-flask-compared)
17. [HTTPS and TLS](#17-https-and-tls)
18. [`requests`](#18-requests)
19. [`httpx`](#19-httpx)
20. [Timeouts](#20-timeouts)
21. [Retries, backoff and jitter](#21-retries-backoff-and-jitter)
22. [A resilient API client, step by step](#22-a-resilient-api-client-step-by-step)
23. [Web scraping with BeautifulSoup](#23-web-scraping-with-beautifulsoup)
24. [Being a polite scraper](#24-being-a-polite-scraper)
25. [What happens when you type a URL](#25-what-happens-when-you-type-a-url)
26. [Project: a raw-socket server and a resilient client](#26-project-a-raw-socket-server-and-a-resilient-client)
27. [Common traps](#27-common-traps)
28. [Summary](#28-summary)

## 1. Why networks are hard

### 1.1 A function call that can fail in new ways

Calling a function in your own program is simple. The call happens, it returns or it raises, and that is all. Calling a function **on another computer** (which is what an API request is) adds a long list of new ways to fail:

| What can go wrong | Example | What your code sees |
|---|---|---|
| The name does not exist | typo in the host name | a DNS error |
| Nobody listens at the address | the server program is stopped | "connection refused" |
| The machine does not answer | the cable is cut, or a firewall drops packets | nothing... until a timeout |
| The server accepts, then is too slow | overloaded database | a read timeout |
| The server answers with an error | a bug, or "slow down" | status 500 or 429 |
| The connection breaks halfway | Wi-Fi drops | a reset or a short read |
| The answer arrives but you never see it | the reply is lost | you do not know if it worked |

The last row is the most important lesson of this chapter. If you send "charge the card" and the connection dies before the reply arrives, **you cannot tell** whether the card was charged. This one fact shapes everything about retries (sections 21 and 22).

### 1.2 The eight fallacies

Engineers at Sun Microsystems once listed beliefs that beginners hold about networks and that are all false. They are worth learning:

1. The network is reliable.
2. Latency is zero.
3. Bandwidth is infinite.
4. The network is secure.
5. Topology does not change.
6. There is one administrator.
7. Transport cost is zero.
8. The network is homogeneous.

Every technique in this chapter answers one of them: **timeouts** answer 1 and 2, **TLS** answers 4, **retries** answer 1, and **DNS** answers 5.

### 1.3 What you will build, in order

```text
  sockets (bytes)  -->  HTTP (text rules)  -->  JSON APIs  -->  clients that survive failure
   sections 5-6          sections 7-12           section 14       sections 18-22
```

We start at the bottom on purpose. If you know that HTTP is "just text on a socket", then `requests` stops being magic, and a bug like "the response is cut in half" becomes easy to understand.

## 2. The layers model

### 2.1 Why layers

Sending a web page from a server in Mumbai to a phone in Pune involves cables, radio, routers, addresses, reliability, security and a page format. No single program does all of that. The job is **split into layers**. Each layer solves one problem and uses the layer below it as a black box.

Think of posting a letter. You write the letter (your message). You put it in an envelope with an address (the postal system's format). The post office sorts envelopes into bags for trucks (routing). A truck driver drives on roads (the physical link). You never think about the roads when you write the letter, and the driver never reads the letter.

### 2.2 The four layers we use

The internet follows the **TCP/IP model**. We use its four layers:

```text
  Layer           Question it answers              Examples            You meet it as
  --------------  -------------------------------  ------------------  ----------------------
  Application     What do we say to each other?    HTTP, DNS, TLS*     requests.get(...)
  Transport       How does data reach the right    TCP, UDP            socket.socket(...)
                  program, and how reliably?
  Internet        How does a packet find the       IP (IPv4, IPv6)     "127.0.0.1", "10.0.0.5"
                  right computer across networks?
  Link            How do bits move over one hop    Wi-Fi, Ethernet     (your driver; invisible)
                  (cable, radio)?
  (* TLS sits between application and transport; see section 17)
```

Each layer **wraps** the data of the layer above, like envelopes inside envelopes:

```text
  +-----------+------------+------------+--------------------------------------+
  | Link hdr  | IP header  | TCP header |  HTTP message: "GET /hello HTTP/1.1" |
  | (hop)     | (computers)| (programs) |  (what the app says)                 |
  +-----------+------------+------------+--------------------------------------+
   ^ link layer  ^ internet    ^ transport   ^ application layer (the payload)
```

The names you will see again and again:

- A **packet** is one IP unit, up to about 1,500 bytes on most links. Big messages are cut into many packets and put together again at the other end.
- A **segment** is a TCP packet. A **datagram** is a UDP packet. For us the words are almost the same.
- The **payload** is the data a layer carries for the layer above.

### 2.3 What each layer promises

| Layer | Promise | What it does NOT promise |
|---|---|---|
| IP | Best effort: "I will try to get this packet there." | No delivery, no order, no copies guarantee |
| UDP | IP plus a port number | Still no delivery guarantee, no order |
| TCP | A reliable, ordered **stream of bytes** | No message boundaries; no speed promise; no deadline |
| HTTP | Requests and responses with meaning | Nothing about whether the other side is honest |

TCP gives you the feeling of a reliable pipe. It does this by numbering bytes, asking for lost ones again (retransmission), and slowing down when the network is crowded. Notice what it does not promise: **time**. If the network is broken, TCP just keeps trying, quietly, for minutes. That is why every network call needs a timeout (section 20).

### 2.4 Where Python sits

- Module `socket`: the transport layer (TCP and UDP) and a little of the internet layer.
- Module `http.client`, `urllib.request`, libraries `requests`, `httpx`: the application layer (HTTP), built on `socket`.
- Module `ssl`: TLS, wrapped around a socket.
- Module `http.server`: the application layer on the server side.

In this chapter we go *down* first (sockets), then *up* (HTTP, clients). Learners who know both ends debug network problems much faster.

## 3. IP addresses, ports and localhost

### 3.1 IP addresses

Every device on a network has an **IP address**, the number that routers use to deliver packets to it. There are two versions:

- **IPv4**: four numbers from 0 to 255, such as `192.168.1.20`. It is a 32-bit number written in "dotted" form. There are about 4.3 billion of them, which turned out not to be enough.
- **IPv6**: eight groups of hexadecimal digits, such as `2001:db8::1` (`::` stands for a run of zeros). It is a 128-bit number. The loopback address is `::1`.

The standard library has a module for working with them, so you never have to split strings:

```python
import ipaddress

for text in ["127.0.0.1", "192.168.1.20", "8.8.8.8", "::1", "2001:db8::1"]:
    ip = ipaddress.ip_address(text)
    print(f"{text:14} v{ip.version}  loopback={ip.is_loopback!s:5}  private={ip.is_private!s:5}  global={ip.is_global}")

print(int(ipaddress.ip_address("192.168.1.20")))        # an IPv4 address is just a number
net = ipaddress.ip_network("192.168.1.0/24")
print(net.num_addresses, ipaddress.ip_address("192.168.1.77") in net, ipaddress.ip_address("192.168.2.1") in net)
```
```text
127.0.0.1      v4  loopback=True   private=True   global=False
192.168.1.20   v4  loopback=False  private=True   global=False
8.8.8.8        v4  loopback=False  private=False  global=True
::1            v6  loopback=True   private=True   global=False
2001:db8::1    v6  loopback=False  private=True   global=False
3232235796
256 True False
```

Four things to read from that output:

- **Loopback** (`127.0.0.0/8`, `::1`): "this computer". Packets sent there never leave the machine.
- **Private** ranges (`10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`): used inside homes and offices. Many homes can reuse the same numbers because these addresses are not routed on the public internet.
- **Global**: public addresses, reachable from anywhere.
- `192.168.1.0/24` is **CIDR notation**: the first 24 bits are the network, the last 8 bits are free for hosts, so the network holds 256 addresses.

(Documentation examples such as `2001:db8::1` are reserved: they are neither global nor useful for real traffic. That is why this chapter can use them freely.)

### 3.2 Ports

An IP address finds a *computer*. But a computer runs many programs that talk to the network: a browser, a mail app, a database. A **port** is a number from 0 to 65535 that picks the *program*. An IP address plus a port, such as `127.0.0.1:5000`, is the full address of one conversation endpoint, called a **socket address**.

```text
   computer 192.168.1.20
   +-----------------------------------------------+
   |  port 22   -> ssh server                      |
   |  port 80   -> web server (HTTP)               |
   |  port 443  -> web server (HTTPS)              |
   |  port 5432 -> PostgreSQL database             |
   |  port 51734-> your browser (a temporary port) |
   +-----------------------------------------------+
```

Port ranges and conventions:

| Range | Name | Notes |
|---|---|---|
| 0 - 1023 | well-known | `80` HTTP, `443` HTTPS, `22` SSH, `53` DNS, `25` mail. On Linux/macOS only a privileged user may listen here |
| 1024 - 49151 | registered | `5432` PostgreSQL, `3306` MySQL, `5000` Flask, `8000` Django/dev servers, `8080` common alternative HTTP |
| 49152 - 65535 | dynamic (ephemeral) | the OS hands these out to *clients* for the other end of a connection |

Every TCP connection is identified by **four** numbers: client IP, client port, server IP, server port. Thousands of browsers can connect to port 443 of one server because each has a different client IP and client port.

### 3.3 Port 0 and why this chapter uses it

If a program binds to port **0**, the operating system picks a free ephemeral port and tells you which. Examples that hard-code `8000` break when something else already uses 8000, and the error (`Address already in use`) confuses beginners. So we always ask for port 0:

```python
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("127.0.0.1", 0))          # port 0: "pick one for me"
    host, port = s.getsockname()
    print(host, "port is an ephemeral one:", 1024 <= port <= 65535)
```
```text
127.0.0.1 port is an ephemeral one: True
```

The real port number is **machine-specific** (it differs every run), so we print a yes/no fact instead.

### 3.4 `localhost`, `127.0.0.1` and `0.0.0.0`

These three look alike and mean different things:

| Text | Meaning | Reachable from other computers? |
|---|---|---|
| `127.0.0.1` | the IPv4 loopback address | No |
| `localhost` | a *name* that normally resolves to `127.0.0.1` (and `::1`) | No |
| `0.0.0.0` | when *binding*: "all my network interfaces" | **Yes**, from your whole network |

Rule for development: **bind to `127.0.0.1`**. Binding to `0.0.0.0` exposes your half-finished program (maybe with debug mode on) to everyone on the same Wi-Fi.

A common bug: your server binds to `localhost`, which resolved to IPv6 `::1`, but your client connects to `127.0.0.1` (IPv4). They never meet. Using the literal `127.0.0.1` on both sides avoids it.

## 4. DNS: names to addresses

### 4.1 Why DNS exists

People remember `example.com`. Routers need `203.0.113.7`. The **Domain Name System (DNS)** is the distributed phone book that turns the first into the second. It is itself a network service (usually UDP port 53), so it too can be slow, wrong or down.

A lookup goes roughly like this:

```text
  your program
      | 1. "what is the address of www.example.com?"
      v
  OS resolver ---> local cache? ---yes---> answer
      | no
      v
  recursive resolver (your ISP, or 8.8.8.8, 1.1.1.1)  --- also has a cache
      | asks, from the top:
      +--> root server:  "ask the .com servers"
      +--> .com server:  "ask the servers of example.com"
      +--> example.com's own server:  "www is 203.0.113.7, keep it for 300 seconds"
```

The last number is the **TTL** (time to live). Caches may keep the answer that many seconds. Short TTLs let a company move a service quickly; long TTLs make lookups fast. This is also why, when someone changes DNS, "it works for me but not for you" happens for a while.

Common record types: `A` (name to IPv4), `AAAA` (name to IPv6), `CNAME` (this name is an alias of another name), `MX` (mail servers), `TXT` (free text, used for verification).

### 4.2 `socket.getaddrinfo`

In Python you rarely ask DNS directly. You call `socket.getaddrinfo(host, port)`, which asks the operating system's resolver. It looks in the `hosts` file first, then in the cache, then asks the network. It returns every way to reach the host, as tuples `(family, type, proto, canonname, sockaddr)`.

The name `localhost` is answered from the `hosts` file, so this runs offline:

```python
import socket

# family=AF_INET asks for IPv4 only, so the result is the same on every machine
for family, type_, proto, canon, sockaddr in socket.getaddrinfo(
        "localhost", 8080, family=socket.AF_INET, type=socket.SOCK_STREAM):
    print(family.name, type_.name, sockaddr)

print(socket.getaddrinfo("127.0.0.1", 80, type=socket.SOCK_STREAM)[0][4])   # an IP literal needs no lookup
print(socket.gethostbyname("localhost"))                                      # older, IPv4-only helper
```
```text
AF_INET SOCK_STREAM ('127.0.0.1', 8080)
('127.0.0.1', 80)
127.0.0.1
```

Why it returns a *list*: a host can have several addresses (IPv4 and IPv6, or several servers for load sharing). A good client tries them in order. `socket.create_connection((host, port))` does exactly that for you, and it is what you should use instead of calling `socket.socket(...).connect(...)` yourself.

If the name cannot be resolved, you get `socket.gaierror` ("get address info error"), a subclass of `OSError`. A name ending in `.invalid` is reserved by the standard and never exists, so it is safe to test with:

```python
import socket

try:
    socket.getaddrinfo("no-such-host.invalid", 80)
except socket.gaierror as exc:
    print("type:", type(exc).__name__, "| is OSError:", isinstance(exc, OSError))
    # exc.errno / exc.strerror differ between operating systems: machine-specific
```
```text
type: gaierror | is OSError: True
```

#### Try it on your machine: a real DNS lookup (needs the internet)

Nothing here was run offline, because it needs a working connection. Run it yourself:

```text
$ python -c "import socket; print(socket.getaddrinfo('example.com', 443, type=socket.SOCK_STREAM))"
```

Expected shape of the output (the addresses, the number of lines and the order are **machine-specific** and change over time; `203.0.113.7` and `2001:db8::7` below are invented documentation values):

```text
[(AddressFamily.AF_INET6, SocketKind.SOCK_STREAM, 6, '', ('2001:db8::7', 443, 0, 0)),
 (AddressFamily.AF_INET, SocketKind.SOCK_STREAM, 6, '', ('203.0.113.7', 443))]
```

If you also have the `dig` or `nslookup` tool you can see the TTL and the record type: `dig example.com A +noall +answer` prints a line like `example.com. 300 IN A 203.0.113.7`. Here `300` is the TTL in seconds and `A` is the record type.

### 4.3 What DNS means for your code

- **A lookup takes time**, often 10 to 100 ms the first time. HTTP clients keep connections open to avoid repeating it (section 18).
- **A lookup can fail** while the rest of the network is fine. The error is `gaierror`, and `requests` wraps it in `requests.ConnectionError`.
- **A name can map to many addresses**, so "the server's IP" is not a stable idea. Never store an IP in place of a name.
- **The OS resolver is blocking.** In async code a slow lookup can stall a thread (core.21, section 14).

#### Try it 4.1

Predict what this prints on any computer, with or without internet.

```python
import socket
infos = socket.getaddrinfo("localhost", 9, family=socket.AF_INET, type=socket.SOCK_DGRAM)
print(len(infos) >= 1, infos[0][0].name, infos[0][1].name, infos[0][4])
```

<details><summary>Answer</summary>

```text
True AF_INET SOCK_DGRAM ('127.0.0.1', 9)
```

`SOCK_DGRAM` means UDP. The result is a tuple `(address, port)` for IPv4. `localhost` is `127.0.0.1` and the port is the number we asked for.
</details>


## 5. Sockets: TCP and UDP on loopback

### 5.1 What a socket is

A **socket** is an object that represents one end of a network conversation. You create it, connect it, and then **write bytes into it and read bytes out of it**, almost like a file. Everything above this layer (HTTP, `requests`, a web browser) is built from sockets.

The function `socket.socket(family, type)` makes one:

- `family`: `socket.AF_INET` for IPv4 (`AF_INET6` for IPv6).
- `type`: `socket.SOCK_STREAM` for **TCP**, `socket.SOCK_DGRAM` for **UDP**.

A socket is a resource like a file: it must be closed. Use `with`, exactly as with `open` (core.10).

### 5.2 UDP: letters in the post

UDP is the simple one. There is no connection. You address a **datagram** (one packet of data) to `(ip, port)` and drop it in the box. It may arrive or be lost; if it arrives it is delivered as **one whole message** with its boundaries intact.

```text
  client                                server
  sendto(b"ping", addr) ----------->    recvfrom(...) -> (b"ping", client_addr)
                        <-----------    sendto(b"PING", client_addr)
  recvfrom(...) -> (b"PING", addr)
```

Here is a complete UDP echo that runs on loopback. The server runs in a background thread, because one program cannot be both a blocked server and a client without threads (core.21).

```python
import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("127.0.0.1", 0))                 # port 0: the OS picks a free port
server_addr = server.getsockname()            # remember where the server lives


def echo_upper():
    for _ in range(2):                        # serve exactly two datagrams, then stop
        data, client_addr = server.recvfrom(1024)
        server.sendto(data.upper(), client_addr)


t = threading.Thread(target=echo_upper)
t.start()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
    client.settimeout(2)                      # never wait forever (section 20)
    for text in [b"ping", b"hello udp"]:
        client.sendto(text, server_addr)
        reply, _ = client.recvfrom(1024)
        print(text, "->", reply)

t.join()
server.close()
```
```text
b'ping' -> b'PING'
b'hello udp' -> b'HELLO UDP'
```

What to notice:

- `bind` gives the server socket a fixed address; the **client never binds**. The OS gives it an ephemeral port automatically at the first `sendto`.
- `recvfrom` returns the data **and the sender's address**, so the server knows where to reply.
- `b"hello udp"` came back as exactly one message. UDP keeps boundaries.
- On a real network a datagram can vanish, so real UDP programs add their own timeouts and retries. On loopback, loss almost never happens, which is why this demo works every time. DNS, video calls and games use UDP: they prefer "fast and maybe lossy" to "slow and perfect".

### 5.3 TCP: a phone call

TCP is the one HTTP uses. First the two sides **establish a connection**, then they exchange a reliable, ordered stream of bytes, then they close it. The server needs two kinds of socket:

- a **listening socket**: waits for new callers (`bind`, `listen`, `accept`);
- a **connection socket** per caller: the one you actually `recv` from and `send` to. `accept()` returns it.

```text
  server                                         client
  ------                                         ------
  s = socket()
  s.bind(("127.0.0.1", 0))
  s.listen()                  <- ready for callers
  conn, addr = s.accept()  ...blocks...          c = socket.create_connection(server_addr)
                              <---- SYN ------   (1) "can we talk?"
                              ----- SYN+ACK -->  (2) "yes, can you hear me?"
                              <---- ACK ------   (3) "yes"       connection open
  conn.recv(1024) <-------------- bytes -------- c.sendall(b"...")
  conn.sendall(b"...") ---------- bytes ------>  c.recv(1024)
  conn.close() / c.close()    <---- FIN/ACK ---> either side may close; the other sees b""
```

The three steps at the top are the **three-way handshake**. It costs one **round trip** (a message there and back) before any data moves. If the server is 100 ms away, every new connection costs 100 ms of waiting. This is the main reason HTTP clients reuse connections.

A complete echo server and client:

```python
import socket
import threading

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(("127.0.0.1", 0))
listener.listen()                         # start accepting callers
server_addr = listener.getsockname()


def serve_one_client():
    conn, client_addr = listener.accept()     # blocks until someone connects
    with conn:
        print("server: client port is ephemeral:", client_addr[1] >= 1024)
        while True:
            data = conn.recv(1024)
            if data == b"":                   # empty bytes = the other side closed
                print("server: client closed the connection")
                break
            conn.sendall(data.upper())        # echo back, upper-cased


t = threading.Thread(target=serve_one_client)
t.start()

with socket.create_connection(server_addr, timeout=2) as client:
    for text in [b"hello", b"tcp is a stream"]:
        client.sendall(text)
        print("client got:", client.recv(1024))

t.join()
listener.close()
```
```text
server: client port is ephemeral: True
client got: b'HELLO'
client got: b'TCP IS A STREAM'
server: client closed the connection
```

Read the code in this order:

1. The **listening socket** is made, bound to port 0, and told to `listen()`. From this moment the operating system accepts connections for it, even before `accept()` is called. Callers wait in a queue (the *backlog*).
2. `accept()` blocks until a client connects, then returns a **new** socket `conn` for that caller and the caller's address.
3. `recv(1024)` means "give me **up to** 1024 bytes, as soon as at least one byte is available". It blocks until something arrives.
4. **`recv` returning `b""` is not an error. It means the other side closed the connection** (end of file for the stream). A loop that does not check for it spins forever.
5. `sendall(data)` sends **all** the bytes. Plain `send` may send only part and returns how many it sent; you would need a loop. Use `sendall`.
6. `socket.create_connection(addr)` is the right way to connect from a client. It resolves names (section 4), tries every address, and applies the timeout.

Two ordinary mistakes with servers, each with a message you will meet:

- `OSError: [Errno 98] Address already in use` (Linux; the number differs on other systems): you started a server on a fixed port that is already taken, often by your own earlier run. A freshly closed port can stay in a "waiting" state for about a minute. For servers that must use a fixed port, call `s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` before `bind`. With port 0 you never see this.
- `ConnectionRefusedError`: the address is valid but nobody listens on that port. Let us see it on purpose. We bind a socket to get a free port, close it so that nobody listens there, and connect:

```python
import socket

probe = socket.socket()
probe.bind(("127.0.0.1", 0))
free_port = probe.getsockname()[1]
probe.close()                                  # now nobody listens on free_port

try:
    socket.create_connection(("127.0.0.1", free_port), timeout=2)
except ConnectionRefusedError as exc:
    print("refused:", type(exc).__name__, "| is OSError:", isinstance(exc, OSError))
```
```text
refused: ConnectionRefusedError | is OSError: True
```

"Refused" is actually a *good* kind of failure: the other computer answered immediately and said "no". The bad kind is silence (a timeout), because you wait the whole timeout before you know.

### 5.4 TCP and UDP compared

| | TCP | UDP |
|---|---|---|
| Connection | yes (handshake) | no |
| Delivery | guaranteed, or you get an error | best effort |
| Order | guaranteed | not guaranteed |
| Message boundaries | **none** (a byte stream) | kept (one datagram = one message) |
| Speed and overhead | slower start, more overhead | faster, light |
| Used by | HTTP, HTTPS, SSH, email, databases | DNS, video calls, games, QUIC (HTTP/3) |

#### Try it 5.1

The server below reads once and sends back the **length** of what it got. The client sends 5 bytes. Predict the two printed lines.

```python
import socket
import threading

listener = socket.socket()
listener.bind(("127.0.0.1", 0))
listener.listen()
addr = listener.getsockname()


def serve():
    conn, _ = listener.accept()
    with conn:
        data = conn.recv(1024)
        conn.sendall(str(len(data)).encode())


t = threading.Thread(target=serve)
t.start()
with socket.create_connection(addr, timeout=2) as c:
    c.sendall("héllo".encode("utf-8"))
    print(c.recv(1024))
    print(len("héllo"))
t.join()
listener.close()
```

<details><summary>Answer</summary>

```text
b'6'
5
```

Sockets move **bytes**, not text. The string `"héllo"` has 5 characters, but `é` takes 2 bytes in UTF-8, so 6 bytes cross the wire. The server counted bytes (`b'6'`); `len` of the string counted characters (`5`). Always `.encode()` before sending and `.decode()` after receiving (core.10 on text and bytes).
</details>

## 6. The byte-stream problem: framing

### 6.1 TCP does not know where your messages start and end

This is the single most important idea in network programming, and the source of the most bugs. Look at what TCP really provides: a **stream of bytes**, like water in a pipe. If you pour in three cups, the other end does not receive "three cups". It receives water. How much comes out per `recv` depends on timing and buffer sizes, not on how you sent it.

Watch it happen. The client sends three separate messages. The server waits until all three have been sent (the `Event`), then reads once:

```python
import socket
import threading

listener = socket.socket()
listener.bind(("127.0.0.1", 0))
listener.listen()
addr = listener.getsockname()
all_sent = threading.Event()


def serve():
    conn, _ = listener.accept()
    with conn:
        all_sent.wait(2)                          # let the three sends happen first
        print("one recv got:", conn.recv(1024))


t = threading.Thread(target=serve)
t.start()
with socket.create_connection(addr, timeout=2) as c:
    c.sendall(b"hello")
    c.sendall(b"world")
    c.sendall(b"!")
    all_sent.set()
    t.join()
listener.close()
```
```text
one recv got: b'helloworld!'
```

Three `sendall` calls, one `recv`, one blob: `b'helloworld!'`. The boundaries are **gone**. If the server expected "one `recv` = one message", it would now think `helloworld!` is a single message.

The opposite also happens: one big message is delivered in several pieces, and `recv(n)` can return fewer than `n` bytes even though more are on the way. The next example sends 100,000 bytes and reads in a loop to count how the data arrives. The number of pieces depends on the machine, so we print only facts that are always true:

```python
import socket
import threading

listener = socket.socket()
listener.bind(("127.0.0.1", 0))
listener.listen()
addr = listener.getsockname()
SIZE = 100_000


def serve():
    conn, _ = listener.accept()
    with conn:
        conn.sendall(b"x" * SIZE)


t = threading.Thread(target=serve)
t.start()
with socket.create_connection(addr, timeout=2) as c:
    pieces = []
    while sum(len(p) for p in pieces) < SIZE:
        chunk = c.recv(4096)                      # asks for at most 4096 bytes
        if not chunk:
            break
        pieces.append(chunk)
    print("total bytes:", sum(len(p) for p in pieces))
    print("arrived in several pieces:", len(pieces) > 1)
    print("no piece larger than asked:", max(len(p) for p in pieces) <= 4096)
t.join()
listener.close()
```
```text
total bytes: 100000
arrived in several pieces: True
no piece larger than asked: True
```

The number of pieces is **machine-specific**; only the total is guaranteed. So the rule is:

> **One `send` does not equal one `recv`.** Never assume it. You must mark where messages start and end yourself. That is called **framing**.

### 6.2 Three ways to frame

| Method | How it works | Used by | Weakness |
|---|---|---|---|
| **Delimiter** | A special byte(s) ends each message, such as `\n` | HTTP headers (`\r\n\r\n`), SMTP, Redis | The data must never contain the delimiter (or must be escaped) |
| **Length prefix** | First write the length, then exactly that many bytes | HTTP bodies (`Content-Length`), most binary protocols | Need a fixed-size length field and careful reading |
| **Close the connection** | The end of the message is the end of the stream | HTTP/1.0 bodies, `Connection: close` | Only one message per connection |

HTTP uses **all three**. Headers end at a blank line (delimiter); the body length is given by `Content-Length` (length prefix); and a server may signal the end by closing.

### 6.3 Reading exactly n bytes

Both delimiter and length framing need one helper: read exactly `n` bytes, however many `recv` calls it takes.

```python
def recv_exactly(sock, n):
    """Read exactly n bytes, or raise if the peer closes early."""
    parts = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(remaining)
        if chunk == b"":
            raise ConnectionError(f"peer closed with {remaining} bytes still expected")
        parts.append(chunk)
        remaining -= len(chunk)
    return b"".join(parts)
```

Study the loop invariant: `remaining` is how many bytes are still owed. Each `recv` may bring fewer than `remaining`, so we loop. The empty `b""` check is not optional: without it a closed connection makes this loop run forever.

### 6.4 A length-prefixed protocol

Let us build a tiny message protocol: every message is a **4-byte big-endian length** followed by that many bytes of UTF-8 text. We use `struct` (core.17, section 10) to pack the length. This goes into a file we reuse: `framing.py`.

```python
"""framing.py: length-prefixed messages over a TCP socket."""
import struct

HEADER = struct.Struct(">I")          # big-endian unsigned 32-bit integer = 4 bytes


def recv_exactly(sock, n):
    parts = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(remaining)
        if chunk == b"":
            raise ConnectionError(f"peer closed with {remaining} bytes still expected")
        parts.append(chunk)
        remaining -= len(chunk)
    return b"".join(parts)


def send_message(sock, text):
    payload = text.encode("utf-8")
    sock.sendall(HEADER.pack(len(payload)) + payload)      # length first, then the bytes


def recv_message(sock):
    (length,) = HEADER.unpack(recv_exactly(sock, HEADER.size))
    return recv_exactly(sock, length).decode("utf-8")
```

Now the same three-messages experiment, but with framing. This time the server reads *after* all data has arrived, and still gets three clean messages:

```python
import socket
import threading

from framing import recv_message, send_message

listener = socket.socket()
listener.bind(("127.0.0.1", 0))
listener.listen()
addr = listener.getsockname()
all_sent = threading.Event()


def serve():
    conn, _ = listener.accept()
    with conn:
        all_sent.wait(2)
        for _ in range(3):
            print("server got message:", repr(recv_message(conn)))


t = threading.Thread(target=serve)
t.start()
with socket.create_connection(addr, timeout=2) as c:
    for text in ["hello", "world", "!"]:
        send_message(c, text)
    all_sent.set()
    t.join()
listener.close()
```
```text
server got message: 'hello'
server got message: 'world'
server got message: '!'
```

Even though TCP glued the bytes together, the length prefix tells the reader where each message ends. This is exactly how `Content-Length` lets an HTTP client know where the body ends.

### 6.5 Delimiters and `makefile`

For text protocols, a newline is simpler. A socket can give you a **file-like object** with `sock.makefile("rb")`, and then `readline()` does the delimiter hunting (and the buffering) for you:

```python
import socket
import threading

listener = socket.socket()
listener.bind(("127.0.0.1", 0))
listener.listen()
addr = listener.getsockname()


def serve():
    conn, _ = listener.accept()
    with conn, conn.makefile("rb") as reader:       # a buffered file view of the socket
        for line in reader:                          # iterates line by line until the peer closes
            print("line:", line.rstrip(b"\r\n"))


t = threading.Thread(target=serve)
t.start()
with socket.create_connection(addr, timeout=2) as c:
    c.sendall(b"first line\nsecond ")
    c.sendall(b"line\nthird line\n")
t.join()
listener.close()
```
```text
line: b'first line'
line: b'second line'
line: b'third line'
```

Note that the second message was sent in two pieces (`b"second "` then `b"line\n"`) and still came out as one line. The buffered reader waits for the newline. HTTP is a delimiter protocol (`\r\n` after each header line), and our raw-socket server in section 15 uses exactly this approach for headers, then `read(n)` for the body.

### 6.6 What the empty bytes and errors mean

| You see | It means | Do |
|---|---|---|
| `recv()` returns `b""` | peer closed cleanly (end of stream) | stop reading, close |
| `ConnectionResetError` | peer closed abruptly (crash, or closed with unread data) | treat as a failed call |
| `BrokenPipeError` | you wrote to a connection the peer already closed | same |
| `TimeoutError` (`socket.timeout`) | nothing arrived within the timeout | retry or give up (section 21) |

In a client, an early `b""` in the *middle* of a message is the "short read" failure: the server promised 500 bytes and the connection closed after 300. `recv_exactly` turns that into a clear `ConnectionError`.

#### Try it 6.1

What exact bytes does `send_message(sock, "hi")` put on the wire under the protocol of section 6.4? Work it out by hand first, then check.

```python
from framing import HEADER

print(HEADER.pack(2) + "hi".encode())
print(len(HEADER.pack(2) + "hi".encode()))
```

<details><summary>Answer</summary>

```text
b'\x00\x00\x00\x02hi'
6
```

The header is the number 2 as four big-endian bytes, `\x00\x00\x00\x02`. Then come the two bytes of `hi`. Six bytes in total: 4 bytes of overhead for a 2-byte message. Because the length is fixed at 4 bytes, one message can be at most 4 GiB. Real servers also set a **maximum** and refuse bigger lengths, otherwise a hostile client could announce "4 billion bytes follow" and make your server wait or allocate memory.
</details>


## 7. HTTP is text on a TCP stream

### 7.1 The idea

**HTTP** (HyperText Transfer Protocol) is the language web clients and servers speak. The big secret: it is plain **text** sent over a TCP connection. A client writes a few lines. The server reads them and writes a few lines back. That is all. Once you have seen it, `requests.get(...)` is no longer magic: it is a convenient way to write those lines.

To experiment safely we need a local server and a few helpers. Save the following as `netlab.py` next to your scripts. The chapter's examples import it. Read it once: it uses only things you already know (`http.server` from core.17, threads from core.21, `contextmanager` from core.10, `http.client` from the standard library, which we meet properly in section 8).

```python
"""netlab.py: helpers for the examples in the Networking chapter (loopback only)."""
import http.client
import json
import socket
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

FIXED_DATE = "Sat, 07 Nov 2026 10:00:00 GMT"      # real servers send the real time


class LabHandler(BaseHTTPRequestHandler):
    """Base class for our demo servers: quiet, repeatable and HTTP/1.1."""
    protocol_version = "HTTP/1.1"                  # allows keep-alive (section 15)

    def version_string(self):
        return "netlab/1.0"

    def date_time_string(self, timestamp=None):    # fixed, so the output never changes
        return FIXED_DATE

    def log_message(self, format, *args):          # no log lines on stderr
        pass

    def read_body(self):
        return self.rfile.read(int(self.headers.get("Content-Length", 0)))

    def reply(self, status, body=b"", content_type="text/plain; charset=utf-8", headers=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        if content_type:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def reply_json(self, status, obj, headers=None):
        self.reply(status, json.dumps(obj), "application/json", headers)


class EchoHandler(LabHandler):
    """Answers every request with a JSON description of what it received."""

    def handle_any(self):
        parts = urlsplit(self.path)
        self.reply_json(200, {
            "method": self.command,
            "path": parts.path,
            "query": parse_qs(parts.query),
            "content_type": self.headers.get("Content-Type"),
            "body": self.read_body().decode("utf-8"),
        })

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = handle_any


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):      # a client that hung up is not news
        pass


@contextmanager
def serve(handler_class):
    """Run handler_class on 127.0.0.1 and a free port; yield its base URL."""
    server = QuietServer(("127.0.0.1", 0), handler_class)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def port_of(base):
    return urlsplit(base).port


@contextmanager
def spy(response=b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok"):
    """A raw server that records the bytes of every request and sends back `response`."""
    seen = []
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.settimeout(0.1)
    stop = threading.Event()

    def loop():
        while not stop.is_set():
            try:
                conn, _ = listener.accept()
            except (TimeoutError, OSError):
                continue
            with conn:
                conn.settimeout(2)
                data = b""
                try:
                    while b"\r\n\r\n" not in data:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    head, _, rest = data.partition(b"\r\n\r\n")
                    length = 0
                    for line in head.split(b"\r\n")[1:]:
                        if line.lower().startswith(b"content-length:"):
                            length = int(line.split(b":")[1])
                    while len(rest) < length:
                        rest += conn.recv(4096)
                except OSError:
                    pass
                seen.append(data if length == 0 else head + b"\r\n\r\n" + rest)
                conn.sendall(response)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{listener.getsockname()[1]}", seen
    finally:
        stop.set()
        thread.join()
        listener.close()


def call(base, method, path, obj=None, headers=None):
    """One request with http.client. Returns (status, headers dict, body); JSON is decoded."""
    host, port = base[len("http://"):].split(":")
    conn = http.client.HTTPConnection(host, int(port), timeout=5)
    try:
        body = None if obj is None else json.dumps(obj).encode("utf-8")
        send_headers = dict(headers or {})
        if body is not None:
            send_headers.setdefault("Content-Type", "application/json")
        conn.request(method, path, body=body, headers=send_headers)
        response = conn.getresponse()
        raw = response.read()
        hdrs = {k.lower(): v for k, v in response.getheaders()}
        if "json" in hdrs.get("content-type", "") and raw:
            return response.status, hdrs, json.loads(raw)
        return response.status, hdrs, raw.decode("utf-8")
    finally:
        conn.close()
```

Three pieces matter right now:

- `LabHandler.reply(...)` sends a complete response. It always writes a `Content-Length` header, for a reason you will understand in a few minutes.
- `serve(handler)` is a context manager (core.10): it starts the server in a background thread on a free port, gives you its base URL such as `http://127.0.0.1:PORT`, and stops it when the `with` block ends.
- `FIXED_DATE` and the fixed `Server` name exist **only so that the output in this book is repeatable**. A real server puts the real time in `Date` and its own software name in `Server`.

### 7.2 Writing a request by hand

We now start a server, open a plain TCP socket to it, write an HTTP request as bytes, and print everything that comes back. No HTTP library is used.

```python
import socket
from netlab import LabHandler, port_of, serve


class Hello(LabHandler):
    def do_GET(self):
        self.reply(200, "Hello from the server!\n")


with serve(Hello) as base:
    request = (
        "GET /hello HTTP/1.1\r\n"
        "Host: 127.0.0.1\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii")
    with socket.create_connection(("127.0.0.1", port_of(base)), timeout=2) as s:
        s.sendall(request)
        chunks = []
        while True:
            chunk = s.recv(4096)
            if chunk == b"":              # the server closed: the response is complete
                break
            chunks.append(chunk)

raw = b"".join(chunks)
print(raw)
print("--- line by line ---")
for line in raw.split(b"\r\n"):
    print(line)
```
```text
b'HTTP/1.1 200 OK\r\nServer: netlab/1.0\r\nDate: Sat, 07 Nov 2026 10:00:00 GMT\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 23\r\n\r\nHello from the server!\n'
--- line by line ---
b'HTTP/1.1 200 OK'
b'Server: netlab/1.0'
b'Date: Sat, 07 Nov 2026 10:00:00 GMT'
b'Content-Type: text/plain; charset=utf-8'
b'Content-Length: 23'
b''
b'Hello from the server!\n'
```

That is HTTP. Look at the two halves.

**What we sent** (three lines of text and a blank line):

```text
GET /hello HTTP/1.1          <- request line: what do I want, and which version of the language
Host: 127.0.0.1              <- a header: which website (one server can host many)
Connection: close            <- a header: "close the connection when you are done"
(blank line)                 <- the end of the headers
```

**What came back:**

```text
HTTP/1.1 200 OK              <- status line: version, a number, a short reason
Server: netlab/1.0           <- headers...
Date: Sat, 07 Nov 2026 ...
Content-Type: text/plain; charset=utf-8
Content-Length: 23
(blank line)
Hello from the server!       <- the body: exactly 23 bytes
```

Every line ends with the two characters **CRLF** (`\r\n`, carriage return and line feed), not just `\n`. The **blank line** (`\r\n\r\n`) marks the end of the headers. Everything after it is the body, and its length is told by `Content-Length`. These are the delimiter and length framings from section 6.2, used together.

### 7.3 Why `Connection: close` was there

HTTP/1.1 connections are **persistent** by default (keep-alive): after the response, the server keeps the TCP connection open, hoping you will send another request on it. That saves the handshake (section 5.3) for every page. But then our `recv` loop would never see `b""`; it would wait for more bytes. Watch what happens when we leave the header out and use a short timeout:

```python
import socket
from netlab import LabHandler, port_of, serve


class Hello(LabHandler):
    def do_GET(self):
        self.reply(200, "Hello from the server!\n")


with serve(Hello) as base:
    request = b"GET /hello HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"          # no Connection: close
    with socket.create_connection(("127.0.0.1", port_of(base)), timeout=0.5) as s:
        s.sendall(request)
        data = b""
        while b"Hello from the server!" not in data:                      # read the whole response
            data += s.recv(4096)
        print(data.split(b"\r\n")[0])                                      # the response arrives...
        try:
            s.recv(4096)                                                   # ...but no end-of-stream
        except TimeoutError:
            print("still open: the server is waiting for my next request")
```
```text
b'HTTP/1.1 200 OK'
still open: the server is waiting for my next request
```

So how does a real client know that the response is complete without waiting for a close? **By reading `Content-Length`.** It reads the headers, finds `Content-Length: 23`, and reads exactly 23 more bytes (our `recv_exactly` from section 6.3). That is why a server must send an accurate `Content-Length`, and why a wrong one is a classic bug: too small and the client cuts the page, too large and the client waits for bytes that never come.

### 7.4 The same thing with `curl`

`curl` is a command-line HTTP client installed on most systems (Windows 10+ includes `curl.exe`; macOS and Linux have it). With `-i` it prints the response headers too. This example calls it from Python against our local server, only if `curl` exists on your machine:

```python
import shutil
import subprocess
from netlab import LabHandler, serve


class Hello(LabHandler):
    def do_GET(self):
        self.reply(200, "Hello from the server!\n")


if shutil.which("curl") is None:
    print("curl is not installed here: skip this example")
else:
    with serve(Hello) as base:
        out = subprocess.run(["curl", "-si", base + "/hello"], capture_output=True, text=True, timeout=10)
    print(out.stdout.replace("\r", ""))
```
```text
HTTP/1.1 200 OK
Server: netlab/1.0
Date: Sat, 07 Nov 2026 10:00:00 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 23

Hello from the server!
```

(`-s` is silent, to hide the progress bar. We removed `\r` only to print neatly.) The tool shows the same text we wrote by hand. When something is wrong with an API, `curl -i URL` is the fastest way to see the truth, before blaming your Python code. `curl -v` additionally prints the request it sent.

#### Try it on your machine: your own server and curl

In one terminal start the standard library's static file server (it listens on 127.0.0.1 only, and port 0 makes it choose a free port):

```text
$ python -m http.server 0 --bind 127.0.0.1
Serving HTTP on 127.0.0.1 port 41233 (http://127.0.0.1:41233/) ...
```

The port (`41233` here) is **machine-specific**. In a second terminal use that port:

```text
$ curl -i http://127.0.0.1:41233/
```

Expected: a `200 OK` status line, headers including `Content-type: text/html; charset=utf-8` and a `Content-Length`, and an HTML page that lists the files of the folder where you started the server. Press `Ctrl+C` in the first terminal to stop it. In the server terminal you also see one log line per request.

#### Try it 7.1

Predict the status line and the body. The request line says `GET /anything?x=1 HTTP/1.1`, and the handler answers with the path it received.

```python
import socket
from netlab import LabHandler, port_of, serve


class Hello(LabHandler):
    def do_GET(self):
        self.reply(200, "path was " + self.path)


with serve(Hello) as base:
    with socket.create_connection(("127.0.0.1", port_of(base)), timeout=2) as s:
        s.sendall(b"GET /anything?x=1 HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")
        data = b""
        while chunk := s.recv(4096):
            data += chunk
print(data.split(b"\r\n")[0])
print(data.split(b"\r\n\r\n", 1)[1])
```

<details><summary>Answer</summary>

```text
b'HTTP/1.1 200 OK'
b'path was /anything?x=1'
```

The status line is `HTTP/1.1 200 OK`. The body repeats the **request target** exactly as written, including the query string: `path was /anything?x=1`. The server receives the path and the query as one string and must split them itself (section 13).
</details>

## 8. Anatomy of a request and a response

### 8.1 The request message

```text
  METHOD  SP  request-target  SP  HTTP-version  CRLF       <- request line
  Header-Name: value                              CRLF       <- zero or more headers
  Header-Name: value                              CRLF
                                                  CRLF       <- blank line
  body (optional)                                            <- bytes, length from Content-Length

  Example:
  POST /items?draft=1 HTTP/1.1
  Host: api.example.com
  Content-Type: application/json
  Content-Length: 15

  {"name": "tea"}
```

- The **method** says what to do (section 9).
- The **request target** is the path plus optional query string. The scheme (`https`) and host are not in it; the host goes in the `Host` header, so one IP address can serve many sites.
- The **headers** are `Name: value` lines. Names are **case-insensitive** (`content-type` equals `Content-Type`).
- The **body** is optional and mostly used with `POST`, `PUT` and `PATCH`.

### 8.2 The response message

```text
  HTTP-version  SP  status-code  SP  reason-phrase  CRLF     <- status line
  Header-Name: value                                 CRLF
                                                     CRLF
  body                                                       <- length from Content-Length

  Example:
  HTTP/1.1 201 Created
  Content-Type: application/json
  Content-Length: 24
  Location: /items/7

  {"id": 7, "name": "tea"}
```

The reason phrase (`Created`) is only for humans; programs look at the **number**. Because the server may send a body for any status (even for errors, with an explanation), always read the body of an error response: it usually says what is wrong.

### 8.3 Seeing what real libraries send

Let us catch the bytes that four different Python clients put on the wire. `netlab.spy()` is a raw server that records each request and replies `ok`.

```python
import http.client
import urllib.request

import httpx
import requests
from netlab import port_of, spy

with spy() as (base, seen):
    host, port = "127.0.0.1", port_of(base)
    conn = http.client.HTTPConnection(host, port, timeout=2)
    conn.request("GET", "/a")
    conn.getresponse().read()
    conn.close()
    urllib.request.urlopen(base + "/b", timeout=2).read()
    requests.get(base + "/c", timeout=2)
    httpx.get(base + "/d", timeout=2)

for raw in seen:
    head = raw.decode("ascii").split("\r\n")
    names = [line.split(":")[0] for line in head[1:] if line]
    print(head[0], "|", ", ".join(names))
```
```text
GET /a HTTP/1.1 | Host, Accept-Encoding
GET /b HTTP/1.1 | Accept-Encoding, Host, User-Agent, Connection
GET /c HTTP/1.1 | Host, User-Agent, Accept-Encoding, Accept, Connection
GET /d HTTP/1.1 | Host, Accept, Accept-Encoding, Connection, User-Agent
```

Four clients, four slightly different requests, all valid HTTP. Notice two things:

- Every one sends `Host`. In HTTP/1.1 it is mandatory.
- `requests` and `httpx` add `Accept`, `Accept-Encoding` (they can decompress gzip) and `User-Agent` for you. `http.client` adds almost nothing: it is the bare minimum.

The `User-Agent` values differ (`python-requests/2.34.2`, `python-httpx/0.28.1`, `Python-urllib/3.14`). Their version numbers are machine-specific.

### 8.4 Where does the body end? Content-Length and chunked

A response body can end in three ways, as in section 6.2:

1. `Content-Length: N`: read exactly N bytes. Most common.
2. **`Transfer-Encoding: chunked`**: the body comes in pieces, each preceded by its size in hexadecimal, ending with a piece of size 0. Used when the server does not know the total size in advance (streaming, generated pages).
3. Connection close: the older HTTP/1.0 way.

A chunked body looks like this (each size line and each piece ends with CRLF). Here is a decoder, built with the helpers we already know:

```python
def decode_chunked(data: bytes) -> bytes:
    """Decode a complete chunked body (no trailers)."""
    out = []
    rest = data
    while True:
        size_line, _, rest = rest.partition(b"\r\n")
        size = int(size_line.split(b";")[0], 16)       # the size is hexadecimal
        if size == 0:
            return b"".join(out)
        out.append(rest[:size])
        rest = rest[size + 2:]                         # skip the data and its CRLF


wire = b"5\r\nHello\r\n7\r\n, World\r\n1\r\n!\r\n0\r\n\r\n"
print(wire)
print(decode_chunked(wire))
print(decode_chunked(b"1a\r\n" + b"x" * 26 + b"\r\n0\r\n\r\n") == b"x" * 26)     # 0x1a is 26
```
```text
b'5\r\nHello\r\n7\r\n, World\r\n1\r\n!\r\n0\r\n\r\n'
b'Hello, World!'
True
```

You almost never write this yourself; `requests`, `httpx` and browsers do it. It is important because it explains how a server can start sending a response before it has computed all of it.

### 8.5 HTTP/1.1, HTTP/2 and HTTP/3

You only need to know the idea. **HTTP/1.1** is the text format above; one request at a time per connection. **HTTP/2** sends the same requests and responses (same methods, headers, status codes) in a binary format and can run many requests at once over one connection. **HTTP/3** does the same on top of UDP (QUIC). The *meaning* does not change, so everything in sections 9 to 14 is true for all versions. We use HTTP/1.1 in this chapter because it is readable.

## 9. Methods: safe and idempotent

### 9.1 What a method says

The method tells the server **what kind of action** you want on the thing named by the URL.

| Method | Meaning | Has a body? | Typical use |
|---|---|---|---|
| `GET` | Read the resource | no | fetch a page, a user, a list |
| `HEAD` | Like GET, but only the headers | no (response has no body) | check size or existence |
| `POST` | Submit data for processing; create a subordinate resource | yes | create an order, upload, login, "do something" |
| `PUT` | **Replace** the whole resource at this URL (or create it) | yes | save a whole record |
| `PATCH` | Change **part** of a resource | yes | update one field |
| `DELETE` | Remove the resource | no | delete a record |
| `OPTIONS` | Ask what is allowed | no | CORS checks, `Allow` header |

### 9.2 Safe and idempotent: two words that matter for retries

Two properties of methods decide what a program may do automatically.

- **Safe**: the request does not change anything on the server (it only reads). `GET`, `HEAD`, `OPTIONS` are safe. Safe means a crawler, a browser prefetching a link, or a retry cannot cause harm.
- **Idempotent**: doing the request **many times has the same effect on the server as doing it once**. (The *response* may differ; the *state* must not.) All safe methods are idempotent. So are `PUT` and `DELETE`.

| Method | Safe | Idempotent |
|---|---|---|
| `GET`, `HEAD`, `OPTIONS` | yes | yes |
| `PUT` | no | **yes** |
| `DELETE` | no | **yes** |
| `POST` | no | **no** |
| `PATCH` | no | not guaranteed (depends on the patch) |

Compare "set the thermostat to 21" (idempotent: ten times is the same as once) with "turn the temperature up by one" (not idempotent: ten times is +10). `PUT` is the first kind; `POST` is usually the second.

Let us prove it with a tiny shop server and watch the state after repeating each request. This uses `netlab.call`, a helper built on `http.client`, that returns `(status, headers, body)`.

```python
import json
from netlab import LabHandler, call, serve


class Shop(LabHandler):
    items = {}                      # id -> item
    next_id = 1

    def do_GET(self):
        self.reply_json(200, self.items)

    def do_POST(self):              # create: the SERVER picks the id
        item = json.loads(self.read_body())
        item_id = str(Shop.next_id)
        Shop.next_id += 1
        self.items[item_id] = item
        self.reply_json(201, {"id": item_id, **item}, {"Location": f"/items/{item_id}"})

    def do_PUT(self):               # replace: the CLIENT names the id in the URL
        item_id = self.path.rsplit("/", 1)[1]
        created = item_id not in self.items
        self.items[item_id] = json.loads(self.read_body())
        self.reply_json(201 if created else 200, self.items[item_id])

    def do_DELETE(self):
        item_id = self.path.rsplit("/", 1)[1]
        if self.items.pop(item_id, None) is None:
            self.reply_json(404, {"error": "no such item"})
        else:
            self.reply(204, b"", content_type=None)


with serve(Shop) as base:
    print("POST twice:")
    for _ in range(2):
        status, _, body = call(base, "POST", "/items", {"name": "tea"})
        print("  ", status, body)
    print("state:", call(base, "GET", "/items")[2])

    Shop.items.clear()
    print("PUT twice:")
    for _ in range(2):
        status, _, body = call(base, "PUT", "/items/7", {"name": "tea"})
        print("  ", status, body)
    print("state:", call(base, "GET", "/items")[2])

    print("DELETE twice:")
    for _ in range(2):
        status, _, body = call(base, "DELETE", "/items/7")
        print("  ", status, repr(body))
    print("state:", call(base, "GET", "/items")[2])
```
```text
POST twice:
   201 {'id': '1', 'name': 'tea'}
   201 {'id': '2', 'name': 'tea'}
state: {'1': {'name': 'tea'}, '2': {'name': 'tea'}}
PUT twice:
   201 {'name': 'tea'}
   200 {'name': 'tea'}
state: {'7': {'name': 'tea'}}
DELETE twice:
   204 ''
   404 {'error': 'no such item'}
state: {}
```

Read it carefully:

- **POST twice** made **two** items (ids 1 and 2). Every repeat changed the state. Not idempotent.
- **PUT twice** left exactly one item `7`. The first response was `201 Created`, the second `200 OK`, but the **state on the server** was the same after one call and after two. Idempotent.
- **DELETE twice**: the first said `204 No Content`, the second `404 Not Found`. The responses differ, but the state ("item 7 does not exist") is the same after both. Idempotent. This is the usual confusion: idempotency is about the **effect on the server**, not about the response.

### 9.3 Why this matters

Suppose you send `POST /payments` and the connection drops before you see the answer. Did the payment happen? If you retry blindly and it did, the customer is charged twice. If you retry `PUT /users/7` blindly, nothing bad happens. So:

> **Retry safe and idempotent requests freely. Retry `POST` only if you made it idempotent with an idempotency key** (section 21.4).

Also note: `GET` must never change anything, even though nothing technically stops you from writing a `GET /delete?id=5` handler. A link prefetcher, a search-engine crawler or a browser that retries on a flaky connection will happily call it. Real incidents have deleted whole databases that way.

### 9.4 `PUT` vs `POST` for creating

Use `POST /items` when the **server** chooses the new resource's URL (it answers `201 Created` and a `Location` header). Use `PUT /items/7` when the **client** knows the final URL. In practice APIs use `POST` to create far more often.

## 10. Status codes

### 10.1 The five families

The status code is a three-digit number. The first digit is the family, and it is enough to decide what to do in a hurry:

| Family | Meaning | Who is responsible | Typical reaction |
|---|---|---|---|
| `1xx` | Informational | n/a | rarely seen (`100 Continue`, `101 Switching Protocols`) |
| `2xx` | Success | nobody | use the result |
| `3xx` | Redirection | n/a | go to another URL, or use your cache |
| `4xx` | **Client** error | **you** (bad request) | fix the request; **do not retry blindly** |
| `5xx` | **Server** error | the server | maybe retry later |

### 10.2 The codes to know

| Code | Name | When |
|---|---|---|
| `200` | OK | normal success |
| `201` | Created | a new resource was made; `Location` says where |
| `202` | Accepted | work was queued, not done yet |
| `204` | No Content | success, nothing to return (typical for `DELETE`) |
| `301` | Moved Permanently | URL changed for good; `Location` has the new one |
| `302` / `307` | Found / Temporary Redirect | temporary move; `307` keeps the method, old `302` clients often turn `POST` into `GET` |
| `304` | Not Modified | your cached copy is still good (section 11.5) |
| `400` | Bad Request | malformed request or invalid data |
| `401` | Unauthorized | you are **not authenticated** (really means "unauthenticated") |
| `403` | Forbidden | authenticated, but **not allowed** |
| `404` | Not Found | no such resource |
| `405` | Method Not Allowed | wrong method for this URL; response has an `Allow` header |
| `409` | Conflict | clashes with current state (duplicate, version mismatch) |
| `415` | Unsupported Media Type | wrong `Content-Type` |
| `422` | Unprocessable Content | well-formed, but invalid (validation failed) |
| `429` | Too Many Requests | you are rate-limited; `Retry-After` says when to return |
| `500` | Internal Server Error | the server crashed on a bug |
| `502` / `503` / `504` | Bad Gateway / Service Unavailable / Gateway Timeout | a proxy or the server is down, overloaded or slow; often temporary |

Two classic confusions: **401 vs 403** (401: "who are you?", 403: "I know who you are, and no"), and **404 as a security tool** (some servers answer 404 instead of 403 so as not to reveal that a private page exists).

Python also has the names: `http.HTTPStatus.NOT_FOUND` is `404`, with `.phrase` `'Not Found'`.

```python
from http import HTTPStatus

for code in (200, 201, 204, 301, 304, 400, 401, 403, 404, 429, 500, 503):
    s = HTTPStatus(code)
    print(code, s.name, "-", s.phrase)
print(HTTPStatus(503).is_server_error, HTTPStatus(404).is_client_error, HTTPStatus(204).is_success)
```
```text
200 OK - OK
201 CREATED - Created
204 NO_CONTENT - No Content
301 MOVED_PERMANENTLY - Moved Permanently
304 NOT_MODIFIED - Not Modified
400 BAD_REQUEST - Bad Request
401 UNAUTHORIZED - Unauthorized
403 FORBIDDEN - Forbidden
404 NOT_FOUND - Not Found
429 TOO_MANY_REQUESTS - Too Many Requests
500 INTERNAL_SERVER_ERROR - Internal Server Error
503 SERVICE_UNAVAILABLE - Service Unavailable
True True True
```

### 10.3 A server that shows them

This handler answers `/status/<code>` with that code, adding the extra headers that go with the code. The client prints what it sees. `http.client` does **not** follow redirects, so we see the `301` itself.

```python
from netlab import LabHandler, call, serve


class StatusHandler(LabHandler):
    extra = {
        301: {"Location": "/new-home"},
        401: {"WWW-Authenticate": 'Bearer realm="api"'},
        405: {"Allow": "GET, HEAD"},
        429: {"Retry-After": "30"},
        503: {"Retry-After": "5"},
    }

    def do_GET(self):
        code = int(self.path.rsplit("/", 1)[1])
        body = b"" if code in (204, 304) else f"status {code}\n".encode()
        self.reply(code, body, headers=self.extra.get(code))


with serve(StatusHandler) as base:
    for code in (200, 204, 301, 304, 401, 404, 405, 429, 503):
        status, headers, body = call(base, "GET", f"/status/{code}")
        interesting = {k: v for k, v in headers.items() if k in ("location", "www-authenticate", "allow", "retry-after")}
        print(status, repr(body), interesting)
```
```text
200 'status 200\n' {}
204 '' {}
301 'status 301\n' {'location': '/new-home'}
304 '' {}
401 'status 401\n' {'www-authenticate': 'Bearer realm="api"'}
404 'status 404\n' {}
405 'status 405\n' {'allow': 'GET, HEAD'}
429 'status 429\n' {'retry-after': '30'}
503 'status 503\n' {'retry-after': '5'}
```

Look for the pattern: some codes come with **helper headers** that tell the client how to continue: `Location` (go there), `WWW-Authenticate` (how to log in), `Allow` (what is permitted), `Retry-After` (come back in N seconds). A good client reads them.

`204` and `304` have **no body** by definition. That is why our `reply` sent an empty body for them.

### 10.4 What a client should do with each family

```text
  status 2xx  -->  success: read the body
  status 3xx  -->  follow Location (clients usually do this automatically, up to a limit)
  status 400-499 -> your bug (or your login, or your rate): fix; do NOT retry, except 408, 429
  status 500-599 -> their problem: retry only if the request is safe to repeat, with backoff
```

That last line is a preview of section 21.

#### Try it 10.1

A client calls `DELETE /orders/55` and gets `404`. Another time it calls `POST /orders` and gets `422`. For each: is it worth retrying the identical request? Answer, then run the check.

```python
def worth_retrying(method: str, status: int) -> bool:
    idempotent = method in {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}
    transient = status in {408, 429, 500, 502, 503, 504}
    return idempotent and transient

print(worth_retrying("DELETE", 404), worth_retrying("POST", 422))
print(worth_retrying("GET", 503), worth_retrying("POST", 503))
```

<details><summary>Answer</summary>

```text
False False
True False
```

Both `False` for the first line: a `404` or a `422` is the client's mistake, and sending the same request again gets the same answer. On the second line a `GET` that failed with `503` is worth retrying (`True`); a `POST` that failed with `503` is not retried by this simple rule (`False`), because we do not know if the server did part of the work. Section 21 refines this with idempotency keys.
</details>


## 11. Headers that matter

### 11.1 What headers are for

Headers are the **metadata** of a message: what the body is, who is asking, what is allowed, how long to keep it. Names are case-insensitive. Some are for requests, some for responses, some for both.

| Header | Direction | Purpose |
|---|---|---|
| `Host` | request | which site on this server (required in HTTP/1.1) |
| `User-Agent` | request | which software is asking (`python-requests/2.34.2`) |
| `Accept` | request | which formats I can read (`application/json`) |
| `Accept-Encoding` | request | which compressions I understand (`gzip`) |
| `Authorization` | request | credentials (`Bearer <token>`, `Basic <base64>`) |
| `Content-Type` | both | format of the **body** (`application/json`, `text/html; charset=utf-8`) |
| `Content-Length` | both | size of the body in **bytes** |
| `Cache-Control` | both | how long and by whom this may be cached |
| `ETag` / `If-None-Match` | response / request | version tag of a resource, and "only send if changed" |
| `Location` | response | where to go (redirects, created resources) |
| `Set-Cookie` / `Cookie` | response / request | cookies (section 12) |
| `Retry-After` | response | wait this long before trying again |
| `WWW-Authenticate` | response | how to authenticate (with `401`) |

### 11.2 `Content-Type`, and the bytes-versus-text trap

`Content-Type` tells the receiver how to interpret the body bytes. Typical values: `application/json`, `text/html; charset=utf-8`, `text/plain`, `application/x-www-form-urlencoded` (HTML form), `multipart/form-data` (file upload), `image/png`. The `charset` says how to turn bytes into text. If the header is missing or wrong, a client guesses, and non-English text turns into garbage (`cafÃ©`). Sending JSON without `Content-Type: application/json` makes many servers reject it with `415`.

```python
text = "café ₹100"
body = text.encode("utf-8")
print(len(text), "characters,", len(body), "bytes")          # Content-Length counts BYTES
print(body.decode("utf-8"))
print(body.decode("latin-1"))                                # wrong charset: the classic garbage
```
```text
9 characters, 12 bytes
café ₹100
cafÃ© â¹100
```

A very common server bug: `Content-Length: len(text)` instead of `len(body)`. With non-ASCII text the client then cuts the last characters. **Always count bytes after encoding.**

### 11.3 Content negotiation: `Accept`

The same URL can offer several formats. The client lists what it accepts, in order of preference (with optional `q` weights, 0 to 1), and the server picks. If it cannot satisfy any, it answers `406 Not Acceptable`.

```python
from netlab import LabHandler, call, serve


class Negotiating(LabHandler):
    def do_GET(self):
        accept = self.headers.get("Accept", "*/*")
        if "application/json" in accept:
            self.reply_json(200, {"greeting": "hello"})
        elif "text/plain" in accept or "*/*" in accept:
            self.reply(200, "hello\n")
        else:
            self.reply(406, "I only speak json or text\n")


with serve(Negotiating) as base:
    for accept in ("application/json", "text/plain", "*/*", "image/png"):
        status, headers, body = call(base, "GET", "/", headers={"Accept": accept})
        print(f"{accept:18} -> {status} {headers['content-type']:28} {body!r}")
```
```text
application/json   -> 200 application/json             {'greeting': 'hello'}
text/plain         -> 200 text/plain; charset=utf-8    'hello\n'
*/*                -> 200 text/plain; charset=utf-8    'hello\n'
image/png          -> 406 text/plain; charset=utf-8    'I only speak json or text\n'
```

### 11.4 Authentication headers

`Authorization: Bearer <token>` is how most modern APIs identify you: you get a token (an opaque string) after logging in or from a settings page, and send it on every request. `Basic` auth sends `username:password` encoded with base64.

```python
import base64
from netlab import LabHandler, call, serve


class Protected(LabHandler):
    def do_GET(self):
        auth = self.headers.get("Authorization", "")
        if not auth:
            self.reply_json(401, {"error": "login required"}, {"WWW-Authenticate": 'Bearer realm="demo"'})
        elif auth != "Bearer s3cret-token":
            self.reply_json(403, {"error": "this token may not do that"})
        else:
            self.reply_json(200, {"secret": 42})


with serve(Protected) as base:
    print(call(base, "GET", "/")[0:3:2])
    print(call(base, "GET", "/", headers={"Authorization": "Bearer wrong"})[0:3:2])
    print(call(base, "GET", "/", headers={"Authorization": "Bearer s3cret-token"})[0:3:2])

basic = base64.b64encode(b"asha:pa55word").decode()
print("Authorization: Basic", basic)
print("anyone can undo it:", base64.b64decode(basic))
```
```text
(401, {'error': 'login required'})
(403, {'error': 'this token may not do that'})
(200, {'secret': 42})
Authorization: Basic YXNoYTpwYTU1d29yZA==
anyone can undo it: b'asha:pa55word'
```

(`[0:3:2]` picks the status and the body from the tuple.) Two lessons:

- `401` without credentials, `403` with credentials that are not enough.
- **base64 is an encoding, not encryption.** Anyone who sees a `Basic` header reads the password. That is one more reason that credentials must only travel over HTTPS (section 17). Also: never put a token in a URL (`?token=...`): URLs end up in logs, browser history and `Referer` headers. Never print a token in your own logs either.

### 11.5 Caching: `Cache-Control`, `ETag`, `304`

Fetching the same big resource again and again wastes time and money. HTTP has two cooperating tools:

1. **Freshness**: `Cache-Control: max-age=3600` says "this response is good for an hour; do not even ask again". `no-store` says "never keep this" (for private data). `no-cache` means "keep it but ask me before using".
2. **Validation**: the server sends a version tag `ETag: "abc123"`. Next time the client asks with `If-None-Match: "abc123"`. If nothing changed, the server answers **`304 Not Modified` with no body**: a tiny reply instead of the whole resource.

```python
import hashlib
from netlab import LabHandler, call, serve

PAGE = {"text": "version one"}


class Cached(LabHandler):
    def do_GET(self):
        body = PAGE["text"].encode()
        etag = '"' + hashlib.sha1(body).hexdigest()[:8] + '"'
        if self.headers.get("If-None-Match") == etag:
            self.reply(304, b"", content_type=None, headers={"ETag": etag})
        else:
            self.reply(200, body, headers={"ETag": etag, "Cache-Control": "max-age=60"})


with serve(Cached) as base:
    status, headers, body = call(base, "GET", "/")
    print(status, headers["etag"], headers["cache-control"], repr(body))
    etag = headers["etag"]

    status, headers, body = call(base, "GET", "/", headers={"If-None-Match": etag})
    print(status, repr(body), "<- nothing re-sent")

    PAGE["text"] = "version two"                       # the page changes on the server
    status, headers, body = call(base, "GET", "/", headers={"If-None-Match": etag})
    print(status, headers["etag"] != etag, repr(body))
```
```text
200 "938fe718" max-age=60 'version one'
304 '' <- nothing re-sent
200 True 'version two'
```

The hash of the content is a simple, honest ETag: same content, same tag. Browsers and good API clients do this dance automatically. For you as an API client, the rule is: **respect `Cache-Control` for data that rarely changes, and use `ETag` to make polling cheap**.

#### Try it 11.1

The server below sends `Content-Length: len(text)`. Predict what `http.client` reads, and how many bytes the response really had.

```python
import socket
import threading
import http.client

text = "₹50"
body = text.encode("utf-8")
resp = (b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(text)).encode() + b"\r\nConnection: close\r\n\r\n" + body)

listener = socket.socket()
listener.bind(("127.0.0.1", 0))
listener.listen()


def serve_once():
    conn, _ = listener.accept()
    with conn:
        conn.recv(4096)
        conn.sendall(resp)


threading.Thread(target=serve_once).start()
c = http.client.HTTPConnection("127.0.0.1", listener.getsockname()[1], timeout=2)
c.request("GET", "/")
r = c.getresponse()
data = r.read()
print(len(body), len(data), data)
c.close()
listener.close()
```

<details><summary>Answer</summary>

```text
5 3 b'\xe2\x82\xb9'
```

`₹` takes 3 bytes in UTF-8, so the body has 5 bytes, but the header promised 3 (the number of *characters*). The client trusts the header and reads only 3 bytes: `b'\xe2\x82\xb9'`, which is just the `₹` sign. The `50` is silently lost. A wrong `Content-Length` rarely raises an error; it quietly damages data.
</details>

## 12. Cookies and sessions

### 12.1 The problem: HTTP forgets

Every HTTP request is independent. The server does not remember that you logged in a second ago. The protocol is called **stateless**. To build "logged in" or "shopping cart" on top, the server hands the client a small piece of text, a **cookie**, and the client sends it back with every later request to that site.

```text
  client                                       server
  POST /login  (user, password)  ----------->
                                 <-----------  200 OK
                                               Set-Cookie: sid=s1; HttpOnly; Path=/
  GET /me                        ----------->
  Cookie: sid=s1                               "sid s1 is Asha's session"
                                 <-----------  200 {"user": "asha"}
```

The word **session** means the server-side memory behind the cookie: a table `session id -> data` (who is logged in, what is in the cart). The cookie holds only the (hard to guess) id. The alternative is to put the data itself in the cookie and sign it so it cannot be forged; that is a *signed cookie* (Flask's default session).

### 12.2 `Set-Cookie` attributes

A response line looks like `Set-Cookie: sid=abc123; Max-Age=3600; Path=/; HttpOnly; Secure; SameSite=Lax`. The first pair is the cookie's name and value, and the rest are rules:

| Attribute | Meaning | Why |
|---|---|---|
| `Max-Age=N` / `Expires=date` | lifetime; without it the cookie dies when the browser closes (a *session cookie*) | control how long login lasts |
| `Path=/` | send it only for URLs under this path | scope |
| `Domain=example.com` | also send to subdomains | scope; leave unset for the narrowest rule |
| `Secure` | send only over HTTPS | stop sniffing on plain HTTP |
| `HttpOnly` | JavaScript cannot read it | stop theft through cross-site scripting (XSS) |
| `SameSite=Lax` / `Strict` / `None` | whether to send it on cross-site requests | defence against cross-site request forgery (CSRF) |

The standard library parses them:

```python
from http.cookies import SimpleCookie

jar = SimpleCookie()
jar.load("sid=abc123; Path=/; HttpOnly; SameSite=Lax; Max-Age=3600")
morsel = jar["sid"]
print(morsel.value, "|", morsel["path"], "|", morsel["max-age"], "|", morsel["httponly"], "|", morsel["samesite"])
print(jar.output())
```
```text
abc123 | / | 3600 | True | Lax
Set-Cookie: sid=abc123; HttpOnly; Max-Age=3600; Path=/; SameSite=Lax
```

### 12.3 A login flow, by hand

Our server keeps a dict of sessions. The client below carries the cookie manually, which is exactly what `requests.Session` will do for you in section 18.

```python
import json
from netlab import LabHandler, call, serve


class App(LabHandler):
    sessions = {}                                            # session id -> user name

    def do_POST(self):                                       # POST /login
        user = json.loads(self.read_body())["user"]
        sid = f"s{len(self.sessions) + 1}"                   # real servers use secrets.token_urlsafe(32)
        self.sessions[sid] = user
        self.reply_json(200, {"ok": True}, {"Set-Cookie": f"sid={sid}; HttpOnly; Path=/"})

    def do_GET(self):                                        # GET /me
        cookie = self.headers.get("Cookie", "")
        sid = cookie.partition("sid=")[2].split(";")[0]
        if sid in self.sessions:
            self.reply_json(200, {"user": self.sessions[sid]})
        else:
            self.reply_json(401, {"error": "not logged in"})


with serve(App) as base:
    print(call(base, "GET", "/me")[0::2])                    # no cookie yet
    status, headers, _ = call(base, "POST", "/login", {"user": "asha"})
    print("Set-Cookie header:", headers["set-cookie"])
    sid_cookie = headers["set-cookie"].split(";")[0]         # keep only name=value
    print(call(base, "GET", "/me", headers={"Cookie": sid_cookie})[0::2])
```
```text
(401, {'error': 'not logged in'})
Set-Cookie header: sid=s1; HttpOnly; Path=/
(200, {'user': 'asha'})
```

The pattern is the point: no cookie gives `401`; after the login, the client returns the cookie and gets `200`. **The server sets, the client returns.**

Security rules for session ids: they must be long and random (`secrets.token_urlsafe(32)`, core.17), sent only over HTTPS with `Secure` and `HttpOnly`, and expire. A guessable id (`s1`, `s2`, ...) as in our toy server lets anyone take over other people's sessions.

## 13. URLs and `urllib.parse`

### 13.1 Anatomy

```text
   https://asha:pw@shop.example.com:8443/search/items?q=red+shoes&size=7#reviews
   \___/   \____/ \_______________/ \__/ \_________/ \_____________/ \______/
   scheme  userinfo      host       port    path        query        fragment
```

- **scheme** picks the protocol (`http`, `https`; default ports 80 and 443).
- **host** is a name or an IP; **port** is optional.
- **path** names the resource. **query** passes parameters as `key=value` joined by `&`.
- **fragment** (`#reviews`) is for the browser only. **It is never sent to the server.**

core.17, section 13.1 shows `urlsplit`, `parse_qs`, `urlencode`, `quote` and `urljoin`; reread it if needed. Here are the things that matter for network code.

### 13.2 Never build URLs with string glue

```python
from urllib.parse import quote, urlencode, urlsplit

name = "R&D / café"
bad = f"http://127.0.0.1/search?q={name}&page=1"
print(urlsplit(bad).query)                         # a server splits at each &, so it sees q="R" and a junk key "D / café"

good = "http://127.0.0.1/search?" + urlencode({"q": name, "page": 1})
print(good)
print("path part:", "/files/" + quote("my notes/2026 plan.txt", safe=""))
```
```text
q=R&D / café&page=1
http://127.0.0.1/search?q=R%26D+%2F+caf%C3%A9&page=1
path part: /files/my%20notes%2F2026%20plan.txt
```

An unescaped `&`, `#`, `?`, space or `/` silently changes what the URL means. In bad cases it becomes a **security bug** (a user's input injects extra parameters). Let the library encode: `params={...}` in `requests` and `httpx` does it for you (section 18).

### 13.3 The fragment never leaves the browser

```python
import requests
from netlab import spy

with spy() as (base, seen):
    requests.get(base + "/page?x=1#section-2", timeout=2)
print(seen[0].split(b"\r\n")[0])
```
```text
b'GET /page?x=1 HTTP/1.1'
```

The request line has the path and the query; the `#section-2` was dropped by the client. Servers cannot see it.

#### Try it 13.1

Predict the output.

```python
from urllib.parse import urlsplit, urljoin

u = urlsplit("http://user:pw@127.0.0.1:8080/a/b.html?x=1&x=2#top")
print(u.hostname, u.port, u.username, u.path)
print(urljoin("http://127.0.0.1:8080/a/b.html", "c.html"))
print(urljoin("http://127.0.0.1:8080/a/b.html", "/c.html"))
```

<details><summary>Answer</summary>

```text
127.0.0.1 8080 user /a/b.html
http://127.0.0.1:8080/a/c.html
http://127.0.0.1:8080/c.html
```

`hostname` gives `127.0.0.1`, `port` an `int` 8080, and `username` `user`. `urljoin` replaces the last path segment for a relative link (`/a/c.html`) and replaces the whole path for an absolute-path link (`/c.html`), just like a browser follows links. You will need this in the scraping section.
</details>

## 14. JSON APIs and REST

### 14.1 Why JSON

Programs on different systems need a shared data format. **JSON** (core.17) is text, readable, small, and understood by every language: objects, arrays, strings, numbers, booleans, `null`. A **JSON API** is a set of URLs where you send and receive JSON. In Python, `json.dumps` and `json.loads` convert (core.17); `requests` and `httpx` call them for you through `json=` and `.json()`.

### 14.2 REST in one page

**REST** (Representational State Transfer) is a style for designing HTTP APIs. In practice it comes down to a few rules:

1. **Resources are nouns in URLs**: `/books`, `/books/42`, `/books/42/reviews`. Use plural nouns. Not `/getBook`, not `/deleteBook?id=42`.
2. **The method is the verb**: `GET /books/42` reads, `POST /books` creates, `PUT /books/42` replaces, `PATCH /books/42` changes a part, `DELETE /books/42` removes. The methods have the meaning from section 9.
3. **Status codes carry the result** (section 10): `201` for created, `404` for missing, `422` for invalid data. Do not answer `200` with `{"error": ...}`.
4. **Stateless**: each request carries everything the server needs (token included). No hidden conversation.
5. **Representations**: the JSON you see is a *representation* of the resource, selected by `Accept`/`Content-Type`.
6. **Collections are paged and filterable**: `GET /books?author=Rao&page=2`.
7. **Errors have a consistent shape** that a program can read.
8. **Version** the API (`/v1/books`) so that you can change it without breaking old clients.

| Action | Request | Success | Typical errors |
|---|---|---|---|
| list | `GET /books?page=2` | `200` + list | `400` bad page |
| read | `GET /books/42` | `200` | `404` |
| create | `POST /books` + JSON | `201` + `Location` | `422` invalid, `409` duplicate |
| replace | `PUT /books/42` + JSON | `200` or `204` | `404`, `422` |
| delete | `DELETE /books/42` | `204` | `404` |

Many "REST" APIs are only partly RESTful, and that is fine. The value is **predictability**: a developer who knows one resource knows all of them.

### 14.3 A small API with pagination and errors

```python
import json
from urllib.parse import parse_qs, urlsplit
from netlab import LabHandler, call, serve

BOOKS = {i: {"id": i, "title": f"Book {i}"} for i in range(1, 8)}


class BookApi(LabHandler):
    def error(self, status, code, message):
        self.reply_json(status, {"error": {"code": code, "message": message}})

    def do_GET(self):
        parts = urlsplit(self.path)
        query = parse_qs(parts.query)
        if parts.path == "/v1/books":
            try:
                page = int(query.get("page", ["1"])[0])
                per_page = int(query.get("per_page", ["3"])[0])
            except ValueError:
                return self.error(400, "bad_number", "page and per_page must be integers")
            ids = sorted(BOOKS)
            chunk = ids[(page - 1) * per_page: page * per_page]
            has_next = page * per_page < len(ids)
            self.reply_json(200, {
                "items": [BOOKS[i] for i in chunk],
                "page": page,
                "next": f"/v1/books?page={page + 1}&per_page={per_page}" if has_next else None,
            })
        elif parts.path.startswith("/v1/books/"):
            book = BOOKS.get(int(parts.path.rsplit("/", 1)[1]))
            if book is None:
                self.error(404, "not_found", "no such book")
            else:
                self.reply_json(200, book)
        else:
            self.error(404, "not_found", "unknown path")

    def do_POST(self):
        try:
            data = json.loads(self.read_body())
            title = data["title"]
        except (ValueError, KeyError):
            return self.error(422, "invalid_book", "a JSON object with a 'title' is required")
        new_id = max(BOOKS) + 1
        BOOKS[new_id] = {"id": new_id, "title": title}
        self.reply_json(201, BOOKS[new_id], {"Location": f"/v1/books/{new_id}"})


with serve(BookApi) as base:
    url = "/v1/books"
    while url:                                     # follow "next" until there is none
        status, _, page = call(base, "GET", url)
        print(status, [b["id"] for b in page["items"]], "next =", page["next"])
        url = page["next"]

    print(call(base, "GET", "/v1/books/99")[0::2])
    print(call(base, "GET", "/v1/books?page=x")[0::2])
    status, headers, body = call(base, "POST", "/v1/books", {"title": "New one"})
    print(status, headers["location"], body)
    print(call(base, "POST", "/v1/books", {"name": "wrong field"})[0::2])
```
```text
200 [1, 2, 3] next = /v1/books?page=2&per_page=3
200 [4, 5, 6] next = /v1/books?page=3&per_page=3
200 [7] next = None
(404, {'error': {'code': 'not_found', 'message': 'no such book'}})
(400, {'error': {'code': 'bad_number', 'message': 'page and per_page must be integers'}})
201 /v1/books/8 {'id': 8, 'title': 'New one'}
(422, {'error': {'code': 'invalid_book', 'message': "a JSON object with a 'title' is required"}})
```

What this shows about good design:

- A **list** never returns everything: the client asks page by page, and the response says where the next page is (`next`). A client that loops until `next` is `None` handles any size. Another popular style uses an opaque **cursor** (`?after=abc`) that keeps working even when items are added meanwhile; page numbers can skip or repeat items if data changes during paging.
- **Errors are JSON with a stable `code`**. A program branches on `code` (`not_found`), a human reads `message`.
- Invalid input gives `422`, a missing resource `404`, success on creation `201` with `Location`.
- The URL starts with `/v1`.

### 14.4 Reading an API you did not write

When you meet a new API, check its documentation for: base URL, authentication, rate limits, pagination style, error format, and which calls are idempotent. Try one request with `curl -i` first. Then wrap it in a small client function and put the checks from sections 20 to 22 into that one place.


## 15. Building an HTTP server from raw sockets

You now know enough to write a web server. This is the first half of the module project, and the best way to turn "HTTP is text" from a slogan into a skill. Our server uses only `socket`, `threading` and `json`. It will:

1. accept TCP connections, one thread per connection;
2. read a request: request line, headers, then the body using `Content-Length`;
3. route by method and path, with proper `404`, `405` and `400` answers;
4. write a response with a correct `Content-Length`;
5. keep the connection open (keep-alive) or close it, as the client asks.

### 15.1 The code

Save this as `tinyhttp.py`. Read it top to bottom: every part is something from sections 5 to 10.

```python
"""tinyhttp.py: a small HTTP/1.1 server using only sockets."""
import json
import socket
import threading
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

REASONS = {200: "OK", 201: "Created", 204: "No Content", 400: "Bad Request", 404: "Not Found",
           405: "Method Not Allowed", 500: "Internal Server Error"}
MAX_LINE = 8192                    # longest header line we accept
MAX_BODY = 1_000_000               # largest body we accept


class BadRequest(Exception):
    pass


@dataclass
class Request:
    method: str
    path: str
    query: dict
    version: str
    headers: dict                  # names in lower case
    body: bytes

    def json(self):
        return json.loads(self.body)


def read_request(reader):
    """Read one request from a binary file object. Return None if the client just closed."""
    line = reader.readline(MAX_LINE)
    if line == b"":
        return None
    parts = line.decode("latin-1").rstrip("\r\n").split(" ")
    if len(parts) != 3 or not parts[2].startswith("HTTP/"):
        raise BadRequest("malformed request line")
    method, target, version = parts
    headers = {}
    while True:
        raw = reader.readline(MAX_LINE)
        if raw in (b"\r\n", b"\n"):                      # the blank line: end of the headers
            break
        name, colon, value = raw.decode("latin-1").partition(":")
        if raw == b"" or not colon:
            raise BadRequest("malformed header")
        headers[name.strip().lower()] = value.strip()
    try:
        length = int(headers.get("content-length", "0"))
    except ValueError:
        raise BadRequest("Content-Length is not a number") from None
    if not 0 <= length <= MAX_BODY:
        raise BadRequest("body too large")
    body = reader.read(length)
    if len(body) < length:
        raise BadRequest("body cut short")
    url = urlsplit(target)
    return Request(method, url.path, parse_qs(url.query), version, headers, body)


def build_response(status, body=b"", content_type="text/plain; charset=utf-8",
                   headers=None, keep_alive=True):
    if isinstance(body, (dict, list)):
        body, content_type = json.dumps(body), "application/json"
    if isinstance(body, str):
        body = body.encode("utf-8")                       # Content-Length counts BYTES
    lines = [f"HTTP/1.1 {status} {REASONS.get(status, 'Unknown')}",
             f"Content-Type: {content_type}",
             f"Content-Length: {len(body)}",
             f"Connection: {'keep-alive' if keep_alive else 'close'}"]
    lines += [f"{name}: {value}" for name, value in (headers or {}).items()]
    return "\r\n".join(lines).encode("latin-1") + b"\r\n\r\n" + body


class TinyServer:
    """routes = {"/path": {"GET": function(request) -> (status, body)}}"""

    def __init__(self, routes):
        self.routes = routes
        self.connections = 0                              # how many TCP connections were accepted
        self.requests = 0
        self._stop = threading.Event()
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen()
        self.listener.settimeout(0.1)                     # so the accept loop can notice _stop
        self.port = self.listener.getsockname()[1]
        self.base = f"http://127.0.0.1:{self.port}"

    def __enter__(self):
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        self.listener.close()

    def _accept_loop(self):
        while not self._stop.is_set():
            try:
                conn, _ = self.listener.accept()
            except TimeoutError:
                continue
            self.connections += 1
            threading.Thread(target=self._serve_connection, args=(conn,), daemon=True).start()

    def _serve_connection(self, conn):
        conn.settimeout(5)                                # an idle client cannot hold us forever
        with conn, conn.makefile("rb") as reader:
            while True:
                try:
                    request = read_request(reader)
                except BadRequest as exc:
                    conn.sendall(build_response(400, f"bad request: {exc}\n", keep_alive=False))
                    return
                except OSError:                           # timeout or reset
                    return
                if request is None:                       # client closed the connection
                    return
                self.requests += 1
                connection = request.headers.get("connection", "").lower()
                keep_alive = connection != "close" and request.version == "HTTP/1.1"
                conn.sendall(self._respond(request, keep_alive))
                if not keep_alive:
                    return

    def _respond(self, request, keep_alive):
        methods = self.routes.get(request.path)
        if methods is None:
            return build_response(404, "no such path\n", keep_alive=keep_alive)
        method = "GET" if request.method == "HEAD" else request.method
        handler = methods.get(method)
        if handler is None:
            allowed = ", ".join(sorted(methods))
            return build_response(405, "method not allowed\n", headers={"Allow": allowed},
                                  keep_alive=keep_alive)
        try:
            status, body = handler(request)
        except Exception:                                 # a bug in a handler must not kill the server
            return build_response(500, "internal error\n", keep_alive=keep_alive)
        response = build_response(status, body, keep_alive=keep_alive)
        if request.method == "HEAD":                      # same headers, no body
            response = response.split(b"\r\n\r\n", 1)[0] + b"\r\n\r\n"
        return response
```

### 15.2 How it works

- **`read_request`** is section 6 in action. `readline` finds the end of each line (delimiter framing). The blank line ends the headers. Then `Content-Length` tells it how many body bytes to read (length framing). Anything odd raises `BadRequest`, which becomes a `400`. The limits `MAX_LINE` and `MAX_BODY` stop a hostile client from sending an endless line or a 10 GB body.
- **`build_response`** writes the status line, headers, the blank line and the body, with `Content-Length` computed from the **encoded bytes**.
- **`TinyServer._accept_loop`** accepts connections and gives each to a new thread, so a slow client does not block others. (A thread per connection is simple; real servers use a pool or async I/O, core.21.)
- **`_serve_connection`** loops: read a request, answer, and go on if keep-alive is on. The rule: HTTP/1.1 keeps the connection unless the client says `Connection: close`; HTTP/1.0 closes.
- **`_respond`** routes: unknown path gives `404`, known path with another method gives `405` and an `Allow` header, `HEAD` is answered like `GET` without the body, and an exception in a handler gives `500` without leaking details.

### 15.3 Using it

```python
import http.client
import socket
from netlab import call
from tinyhttp import TinyServer


def hello(request):
    name = request.query.get("name", ["world"])[0]
    return 200, f"Hello, {name}!\n"


def echo(request):
    data = request.json()
    return 201, {"you_sent": data, "keys": sorted(data)}


def crash(request):
    return 1 / 0


routes = {"/hello": {"GET": hello}, "/echo": {"POST": echo}, "/crash": {"GET": crash}}

with TinyServer(routes) as server:
    print(call(server.base, "GET", "/hello?name=Asha")[0::2])
    print(call(server.base, "GET", "/hello")[0::2])
    print(call(server.base, "POST", "/echo", {"b": 1, "a": 2})[0::2])
    print(call(server.base, "GET", "/nope")[0::2])
    status, headers, body = call(server.base, "DELETE", "/hello")
    print(status, headers["allow"])
    print(call(server.base, "GET", "/crash")[0::2])
    status, headers, body = call(server.base, "HEAD", "/hello?name=Asha")
    print("HEAD:", status, headers["content-length"], repr(body))

    # a broken request, typed by hand
    with socket.create_connection(("127.0.0.1", server.port), timeout=2) as s:
        s.sendall(b"THIS IS NOT HTTP\r\n\r\n")
        print(s.recv(4096).split(b"\r\n")[0])
```
```text
(200, 'Hello, Asha!\n')
(200, 'Hello, world!\n')
(201, {'you_sent': {'b': 1, 'a': 2}, 'keys': ['a', 'b']})
(404, 'no such path\n')
405 GET
(500, 'internal error\n')
HEAD: 200 13 ''
b'HTTP/1.1 400 Bad Request'
```

Each of the errors we promised works: `404`, `405` with `Allow`, `500` for a crash, `HEAD` with a length but no body, and `400` for garbage. The server logged nothing and never died.

### 15.4 Keep-alive in numbers

`call()` opens a new TCP connection for every request. A persistent `http.client.HTTPConnection` reuses one. The server counts both:

```python
import http.client
from netlab import call
from tinyhttp import TinyServer

routes = {"/hello": {"GET": lambda request: (200, "hi\n")}}

with TinyServer(routes) as server:
    for _ in range(3):
        call(server.base, "GET", "/hello")
    print("3 calls with call():           connections =", server.connections, "requests =", server.requests)

with TinyServer(routes) as server:
    conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=2)
    for _ in range(3):
        conn.request("GET", "/hello")
        conn.getresponse().read()                 # must read the body before the next request
    conn.close()
    print("3 requests on one connection: connections =", server.connections, "requests =", server.requests)
```
```text
3 calls with call():           connections = 3 requests = 3
3 requests on one connection: connections = 1 requests = 3
```

Three handshakes against one. On a real network each handshake costs a round trip (and an HTTPS handshake costs more, section 17), so reusing connections is a big win. That is why `requests.Session` and `httpx.Client` exist (sections 18 and 19): they keep a pool of open connections.

### 15.5 What is missing (and why you use a framework)

Our server is about 150 lines and it works, but a production server also needs: HTTPS, request timeouts for slow senders, a limit on the number of threads, `Transfer-Encoding: chunked` for request bodies, `Expect: 100-continue`, percent-decoding of paths, protection against path traversal, logging, graceful shutdown, HTTP/2, and a long list of security fixes. This is why you use Flask or Django behind a hardened server such as gunicorn or nginx. Writing the small version once teaches you what those tools do for you.

#### Try it 15.1

What does `build_response(200, "₹")` put on the wire? Predict the whole message, then check the length.

```python
from tinyhttp import build_response

msg = build_response(200, "₹", keep_alive=False)
print(msg)
print(len("₹"), len("₹".encode("utf-8")))
```

<details><summary>Answer</summary>

```text
b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 3\r\nConnection: close\r\n\r\n\xe2\x82\xb9'
1 3
```

The header says `Content-Length: 3` because we measure the encoded bytes (3), not the 1 character. Had we used `len(body)` on the string, the client would read only 1 byte of a 3-byte symbol and see garbage. The same function is what protects you from the bug of section 11.2.
</details>

## 16. `http.server` and Flask, compared

### 16.1 `http.server`

The standard library's `http.server` (used by `netlab`, core.17 section 13.2) does the parsing for you. You subclass `BaseHTTPRequestHandler` and write `do_GET`, `do_POST`, and so on. Points to remember:

- Set `protocol_version = "HTTP/1.1"` if you want keep-alive; the default is HTTP/1.0, which closes after each response. If you do, you must send `Content-Length` yourself.
- Use `ThreadingHTTPServer`, not `HTTPServer`, so one slow client does not freeze the rest.
- The documentation itself says it is **not for production**. Use it for tests, tools and teaching.
- `python -m http.server 0 --bind 127.0.0.1` serves the current folder as a static site. Handy, and also a good way to see why you must never run it in a folder with secrets.

### 16.2 Flask

**Flask** is a small framework: you declare routes with decorators, and it takes care of parsing, JSON, status codes and the details of section 15. It is installed in the course environment. Flask has a *test client* that calls the app **without any network**, which makes it ideal for offline examples:

```python
from flask import Flask, jsonify, request

app = Flask(__name__)
BOOKS = {1: {"id": 1, "title": "Dune"}}


@app.get("/v1/books/<int:book_id>")
def get_book(book_id):
    book = BOOKS.get(book_id)
    if book is None:
        return jsonify(error={"code": "not_found"}), 404
    return jsonify(book)


@app.post("/v1/books")
def create_book():
    data = request.get_json(silent=True)
    if not data or "title" not in data:
        return jsonify(error={"code": "invalid_book"}), 422
    book_id = max(BOOKS) + 1
    BOOKS[book_id] = {"id": book_id, "title": data["title"]}
    return jsonify(BOOKS[book_id]), 201, {"Location": f"/v1/books/{book_id}"}


client = app.test_client()
for response in (client.get("/v1/books/1"), client.get("/v1/books/9"),
                 client.post("/v1/books", json={"title": "Emma"}),
                 client.post("/v1/books", json={"x": 1}),
                 client.delete("/v1/books/1")):
    print(response.status_code, response.get_json(silent=True), response.headers.get("Location"))
```
```text
200 {'id': 1, 'title': 'Dune'} None
404 {'error': {'code': 'not_found'}} None
201 {'id': 2, 'title': 'Emma'} /v1/books/2
422 {'error': {'code': 'invalid_book'}} None
405 None None
```

Compare with section 15: routing, the `405` for the wrong method (the last line, for `DELETE`), JSON parsing, and status codes are done by the framework. The shape of your code is the same: **a function from request to (status, headers, body)**. To run it for real you would use `flask --app yourfile run` (it listens on `127.0.0.1:5000` by default; stop it with `Ctrl+C`). In production a Flask app runs behind a proper server (gunicorn, uWSGI) that provides everything in 15.5.

## 17. HTTPS and TLS

### 17.1 The problem plain HTTP has

Everything in the previous sections travels as **readable text**. Anyone on the path (the Wi-Fi owner, a router, your internet provider) can read your password in a `POST /login`, change the page on its way (inject ads or malware), or pretend to be the server. **HTTPS** is HTTP inside **TLS** (Transport Layer Security, the successor of SSL). TLS gives three guarantees:

| Guarantee | Meaning | Mechanism |
|---|---|---|
| **Confidentiality** | nobody on the path can read the data | encryption with a session key |
| **Integrity** | nobody can change the data unnoticed | message authentication |
| **Authentication** | you are talking to the real `example.com` | a **certificate** the server shows |

TLS sits between TCP and HTTP. HTTP does not change; it just gets a secure pipe.

```text
   Application layer:   HTTP  (same text as before)
   ---------------------------------------------------
   Security layer:      TLS   (encrypts, authenticates)
   ---------------------------------------------------
   Transport layer:     TCP   (reliable byte stream)
   Internet layer:      IP
```

Plain HTTP uses port 80, HTTPS port 443.

### 17.2 The handshake, in outline

```text
  client                                         server
    | --- ClientHello: versions, ciphers, random --->|
    |<-- ServerHello: chosen cipher, random ---------|
    |<-- Certificate: "I am example.com", signed ----|
    |  (client checks the signature chain, the name,  |
    |   and the dates; if bad: STOP with an error)    |
    |<-- key exchange data ---------------------------|
    | --- key exchange data ------------------------>|
    |  both sides now compute the same secret key     |
    | === encrypted HTTP request =====================>|
    |<== encrypted HTTP response ======================|
```

The clever part, key exchange, lets two strangers agree on a secret key **while an eavesdropper watches every message** and still cannot compute it (it uses mathematics such as elliptic-curve Diffie-Hellman). The rest of the conversation is encrypted with that key. TLS 1.3 needs one round trip for this on top of the TCP handshake (TLS 1.2 needed two), and later connections can resume faster.

### 17.3 Certificates and trust

A **certificate** says "this public key belongs to *these names*", valid *between these dates*, signed by an issuer. You trust it because the issuer, a **certificate authority (CA)**, is trusted by your operating system or by the `certifi` bundle that `requests` uses. Certificates form a chain:

```text
  root CA (already in your trust store)
     signs --> intermediate CA
                  signs --> server certificate for example.com
```

Verification checks, at minimum: (1) the chain leads to a trusted root; (2) the certificate's names (the *Subject Alternative Name* list) include the host you asked for; (3) today is within the dates. Any failure raises an error. **The fix is never to switch verification off.**

A **self-signed** certificate is signed by itself, so no CA vouches for it. It is fine for local tests if the client is told to trust that exact certificate, and wrong for the public internet.

### 17.4 TLS on loopback, with a certificate made on your machine

We need a certificate for `127.0.0.1` and `localhost`. The `openssl` command-line tool (installed on Linux and macOS, and with Git for Windows) makes one in a second. This helper file creates it in a temporary folder and starts HTTPS servers. Save it as `tlslab.py`.

```python
"""tlslab.py: a throwaway self-signed certificate and an HTTPS test server (loopback only)."""
import shutil
import socket
import ssl
import subprocess
import tempfile
import threading
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path


def have_openssl():
    return shutil.which("openssl") is not None


def make_cert(folder, names="DNS:localhost,IP:127.0.0.1"):
    """Create cert.pem and key.pem in `folder`, valid for `names`. Return both paths."""
    cert, key = Path(folder) / "cert.pem", Path(folder) / "key.pem"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1",
         "-nodes", "-days", "2", "-subj", "/CN=localhost", "-addext", f"subjectAltName={names}",
         "-keyout", str(key), "-out", str(cert)],
        check=True, capture_output=True)
    return str(cert), str(key)


@contextmanager
def https_server(handler_class, cert, key):
    """Like netlab.serve, but speaking TLS. Yields the https:// base URL."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_class)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"https://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


@contextmanager
def tls_echo_once(cert, key):
    """A raw TLS server that accepts ONE connection and answers 'secure hello'. Yields its port."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()

    def run():
        conn, _ = listener.accept()
        try:
            with context.wrap_socket(conn, server_side=True) as tls:
                tls.recv(1024)
                tls.sendall(b"secure hello")
        except (ssl.SSLError, OSError):
            pass                                    # the client refused the certificate

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        yield listener.getsockname()[1]
    finally:
        thread.join(2)
        listener.close()
```

First, a raw TLS client with the `ssl` module. A *context* holds the rules: which CAs to trust, whether to check names. `ssl.create_default_context()` gives safe defaults (verify the chain, check the host name). We add our own certificate as the one trusted CA.

```python
import socket
import ssl
import tempfile
from tlslab import have_openssl, make_cert, tls_echo_once

if not have_openssl():
    raise SystemExit("openssl is not installed: skip this example")

with tempfile.TemporaryDirectory() as folder:
    cert, key = make_cert(folder)
    context = ssl.create_default_context(cafile=cert)          # trust ONLY our certificate
    with tls_echo_once(cert, key) as port:
        with socket.create_connection(("127.0.0.1", port), timeout=3) as raw:
            with context.wrap_socket(raw, server_hostname="localhost") as tls:
                print("TLS version:", tls.version())            # TLSv1.3 on current systems
                info = tls.getpeercert()
                print("subject:", info["subject"])
                print("names:", info["subjectAltName"])
                tls.sendall(b"hi")
                print("reply:", tls.recv(1024))
```
```text
TLS version: TLSv1.3
subject: ((('commonName', 'localhost'),),)
names: (('DNS', 'localhost'), ('IP Address', '127.0.0.1'))
reply: b'secure hello'
```

`server_hostname` matters twice: it tells the server which certificate to present (many sites share an IP) and it is the **name the certificate must match**. The cipher and exact version are negotiated, so on an old system you might see `TLSv1.2` (machine-specific).

Now the failures. These are the errors you will see in real life, so recognise them.

```python
import socket
import ssl
import tempfile
from tlslab import have_openssl, make_cert, tls_echo_once

if not have_openssl():
    raise SystemExit("openssl is not installed: skip this example")


def try_connect(context, hostname, cert, key):
    with tls_echo_once(cert, key) as port:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=3) as raw:
                with context.wrap_socket(raw, server_hostname=hostname) as tls:
                    tls.sendall(b"hi")
                    return tls.recv(1024)
        except ssl.SSLCertVerificationError as exc:
            return f"REFUSED: {exc.verify_message}"


with tempfile.TemporaryDirectory() as folder:
    cert, key = make_cert(folder)
    print("1.", try_connect(ssl.create_default_context(), "localhost", cert, key))              # no trust
    print("2.", try_connect(ssl.create_default_context(cafile=cert), "bank.example", cert, key))  # wrong name
    print("3.", try_connect(ssl.create_default_context(cafile=cert), "localhost", cert, key))     # correct
```
```text
1. REFUSED: self-signed certificate
2. REFUSED: Hostname mismatch, certificate is not valid for 'bank.example'.
3. b'secure hello'
```

1. **Unknown CA.** Our certificate is signed by nobody the system trusts, so the default context refuses. In real life this appears with company proxies, misconfigured servers and expired intermediates.
2. **Wrong name.** The certificate is valid and trusted, but not for `bank.example`. This is the check that stops an attacker from presenting *their* valid certificate for *their* site while you think you are visiting your bank.
3. Correct trust and correct name: success.

Many learners "fix" error 1 by turning verification off (`verify=False`, `ssl._create_unverified_context()`, `CERT_NONE`). Then the connection is encrypted but **not authenticated**: you talk privately to whoever answers, including an attacker. Never ship that.

### 17.5 HTTPS with `requests`

A full HTTPS web server on loopback, with `requests` as client. `verify=` can be `True` (use the standard trust store), `False` (do not check: avoid) or the **path to a certificate file** to trust.

```python
import tempfile
import warnings

import requests
from netlab import LabHandler
from tlslab import have_openssl, https_server, make_cert

if not have_openssl():
    raise SystemExit("openssl is not installed: skip this example")


class Hello(LabHandler):
    def do_GET(self):
        self.reply_json(200, {"secure": True})


with tempfile.TemporaryDirectory() as folder:
    cert, key = make_cert(folder)
    with https_server(Hello, cert, key) as base:
        print(requests.get(base + "/", verify=cert, timeout=3).json())
        try:
            requests.get(base + "/", timeout=3)                      # default: use the system trust store
        except requests.exceptions.SSLError as exc:
            print("default verify refused:", type(exc).__name__)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            r = requests.get(base + "/", verify=False, timeout=3)     # DO NOT do this outside a test
            print("verify=False worked:", r.status_code, "| warning:", caught[0].category.__name__)
```
```text
{'secure': True}
default verify refused: SSLError
verify=False worked: 200 | warning: InsecureRequestWarning
```

The warning is `urllib3`'s way of shouting "you turned off the safety". Keep it visible.

#### Try it on your machine: a real HTTPS site (needs the internet)

None of this was captured offline. To see a real certificate chain run:

```text
$ python -c "import ssl; print(ssl.get_server_certificate(('example.com', 443))[:60])"
-----BEGIN CERTIFICATE-----
MIII...                      (the first 60 characters: the base64 text differs per site and over time)
$ curl -vI https://example.com 2>&1 | grep -E "SSL connection|subject|issuer|expire"
```

Expected: lines such as `SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384`, a `subject:` containing the site name, an `issuer:` naming a public certificate authority, and an `expire date:` some weeks or months ahead. The exact cipher, issuer and dates are **machine-specific and change over time**. If you have `openssl`, `openssl s_client -connect example.com:443 -servername example.com </dev/null` prints the whole chain.

#### Try it 17.1

Why does the second case in the failure demo above (wrong name) fail even though the certificate is trusted? Predict what the same call prints if the certificate had been created with `names="DNS:bank.example"` and the client asked for `localhost`.

<details><summary>Answer</summary>

It would still be refused with a hostname mismatch: trust says "this certificate is genuine", the name check says "it is genuine **for the name I asked for**". Both must pass. Either check alone is useless: a genuine certificate for an attacker's site would otherwise let them impersonate any site.
</details>


## 18. `requests`

### 18.1 Why a library

You have now seen the whole stack by hand. In daily work you will not write sockets. **`requests`** is the classic Python HTTP client: simple, readable, synchronous. It handles URL encoding, JSON, redirects, cookies, gzip, connection reuse and HTTPS verification for you. It is not in the standard library, so it is a dependency (swe.01: put it in `pyproject.toml`).

We need a lab server with a few special behaviours. Save it as `labapi.py`; it builds on `netlab`.

```python
"""labapi.py: a demo API with redirects, cookies and big bodies."""
from netlab import EchoHandler


class Api(EchoHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/redirect":
            self.reply(302, b"", headers={"Location": "/final"})
        elif path == "/final":
            self.reply_json(200, {"where": "final"})
        elif path == "/login":
            self.reply_json(200, {"ok": True}, {"Set-Cookie": "sid=abc; Path=/; HttpOnly"})
        elif path == "/whoami":
            cookie = self.headers.get("Cookie", "")
            self.reply_json(200, {"cookie": cookie})
        elif path == "/big":
            self.reply(200, b"x" * 200_000, "application/octet-stream")
        elif path.startswith("/status/"):
            self.reply(int(path.rsplit("/", 1)[1]), "status page\n")
        else:
            self.handle_any()
```

### 18.2 The basics

```python
import requests
from labapi import Api
from netlab import serve

with serve(Api) as base:
    r = requests.get(base + "/echo", params={"q": "red shoes", "tag": ["a", "b"]}, timeout=5)
    print(r.status_code, r.ok, r.headers["Content-Type"])
    print(r.url.replace(base, "BASE"))                     # params are encoded for you
    print(r.json()["query"])

    r = requests.post(base + "/echo", json={"name": "tea", "price": 15}, timeout=5)
    print(r.status_code, r.json()["content_type"], r.json()["body"])

    r = requests.post(base + "/echo", data={"name": "tea", "price": 15}, timeout=5)   # an HTML form
    print(r.json()["content_type"], r.json()["body"])

    r = requests.get(base + "/echo", headers={"Accept": "application/json", "X-Trace": "t-1"}, timeout=5)
    print(r.request.headers["X-Trace"], "|", type(r.content).__name__, type(r.text).__name__)
```
```text
200 True application/json
BASE/echo?q=red+shoes&tag=a&tag=b
{'q': ['red shoes'], 'tag': ['a', 'b']}
200 application/json {"name": "tea", "price": 15}
application/x-www-form-urlencoded name=tea&price=15
t-1 | bytes str
```

The pieces to memorise:

- `params={...}` builds the query string (lists become repeated keys).
- `json={...}` serialises to JSON **and** sets `Content-Type: application/json`. `data={...}` sends a form (`application/x-www-form-urlencoded`). Mixing them up is a frequent reason for a `415` or `422`.
- `r.status_code`, `r.ok` (True for status below 400), `r.headers` (a case-insensitive dict), `r.json()`, `r.text` (decoded `str`), `r.content` (raw `bytes`), `r.url`, `r.request` (what was sent).
- Always pass **`timeout=`**. This is rule one (section 20).

### 18.3 Errors: two different kinds

An HTTP error status is **not** an exception by default. You must ask for it:

```python
import requests
from labapi import Api
from netlab import serve

with serve(Api) as base:
    r = requests.get(base + "/status/404", timeout=5)
    print("no exception yet:", r.status_code, r.ok)
    try:
        r.raise_for_status()                               # turns 4xx/5xx into an exception
    except requests.HTTPError as exc:
        print("HTTPError:", exc.response.status_code, "|", exc.response.text.strip())

dead = base                                                # the server is stopped now
try:
    requests.get(dead + "/echo", timeout=2)
except requests.ConnectionError as exc:
    print("ConnectionError:", type(exc).__name__)

print([c.__name__ for c in requests.ReadTimeout.__mro__[:4]])
```
```text
no exception yet: 404 False
HTTPError: 404 | status page
ConnectionError: ConnectionError
['ReadTimeout', 'Timeout', 'RequestException', 'OSError']
```

```text
  Exceptions in requests (all inherit from requests.RequestException)
  ConnectionError  --> no HTTP response: refused, DNS failure, reset
  Timeout          --> ConnectTimeout (connecting too slow), ReadTimeout (response too slow)
  HTTPError        --> only raised by raise_for_status(): the server answered 4xx/5xx
  TooManyRedirects, JSONDecodeError, SSLError ...
```

Keep the two worlds apart in your mind. **A response with 500 means the server was reached and answered** (you have headers and a body). **A `ConnectionError` or `Timeout` means you have no answer at all, and you do not know whether the server did the work.** Retry logic (section 21) treats them differently.

### 18.4 `Session`: cookies, defaults and connection reuse

`requests.get` opens a new connection every time. A `Session` keeps connections open (section 15.4), remembers cookies (section 12) and holds default headers.

```python
import requests
from labapi import Api
from netlab import serve

with serve(Api) as base:
    print("no session:", requests.get(base + "/login", timeout=5).cookies.get("sid"),
          requests.get(base + "/whoami", timeout=5).json())

    with requests.Session() as s:                          # closes its connections at the end
        s.headers.update({"User-Agent": "my-course-bot/1.0"})
        s.get(base + "/login", timeout=5)
        print("session:   ", s.get(base + "/whoami", timeout=5).json())
        print("jar:", dict(s.cookies))
        r = s.get(base + "/echo", timeout=5)
        print(r.request.headers["User-Agent"])
```
```text
no session: abc {'cookie': ''}
session:    {'cookie': 'sid=abc'}
jar: {'sid': 'abc'}
my-course-bot/1.0
```

The plain `requests.get` forgot the login cookie; the `Session` returned it. **Use one `Session` per API you call repeatedly.** `Session` has no default timeout, so you still pass `timeout=` on each call or wrap it (section 22).

### 18.5 Redirects and streaming

By default `requests` follows redirects (up to 30) and keeps the chain in `r.history`:

```python
import requests
from labapi import Api
from netlab import serve

with serve(Api) as base:
    r = requests.get(base + "/redirect", timeout=5)
    print(r.status_code, [h.status_code for h in r.history], r.url.replace(base, "BASE"))
    r = requests.get(base + "/redirect", allow_redirects=False, timeout=5)
    print(r.status_code, r.headers["Location"])

    total = 0
    with requests.get(base + "/big", stream=True, timeout=5) as r:       # body NOT read yet
        for chunk in r.iter_content(chunk_size=65536):
            total += len(chunk)
    print("streamed bytes:", total)
```
```text
200 [302] BASE/final
302 /final
streamed bytes: 200000
```

`stream=True` reads the body in pieces as you ask, instead of loading it all into memory. Use it for large downloads (write each chunk to a file) and always use `with` (or `r.close()`) so the connection returns to the pool. Without `stream`, `requests` reads the whole body before returning.

#### Try it 18.1

Predict the output. (Remember: `r.json()` raises on invalid JSON; `raise_for_status()` raises only for 4xx/5xx.)

```python
import requests
from labapi import Api
from netlab import serve

with serve(Api) as base:
    r = requests.get(base + "/status/204", timeout=5)
    print(r.status_code, repr(r.text), r.ok)
    r.raise_for_status()
    print("after raise_for_status")
    try:
        r.json()
    except requests.exceptions.JSONDecodeError:
        print("not JSON")
```

<details><summary>Answer</summary>

```text
204 '' True
after raise_for_status
not JSON
```

The server replied `204`, but our handler wrote a body "status page" (a real `204` must have none; many clients drop it). Here `requests` shows `204 '' True`: `r.text` is empty. `raise_for_status()` is silent for 204, so we reach the next line, and `r.json()` on an empty body raises `JSONDecodeError`, printing `not JSON`. Lesson: check the status (and for `204` do not call `.json()`).
</details>

## 19. `httpx`

### 19.1 requests with more

**`httpx`** has nearly the same API as `requests` and adds what modern code needs: an **async** client, HTTP/2 support (optional), strict and sensible defaults, and the `MockTransport` for offline tests (used in core.21, section 16, which you should reread now: we will not repeat the async basics). Differences you must know:

| | `requests` | `httpx` |
|---|---|---|
| Default timeout | **none (waits forever)** | **5 seconds** |
| Redirects | followed | **not** followed (`follow_redirects=True` to enable) |
| Async | no | yes (`httpx.AsyncClient`) |
| Reuse connections | `Session` | `Client` (use `with`) |
| Offline fake server | extra libraries | built in (`MockTransport`) |
| Raise on bad status | `raise_for_status()` | `raise_for_status()` |

```python
import asyncio
import httpx
from labapi import Api
from netlab import serve

with serve(Api) as base:
    with httpx.Client(base_url=base, timeout=httpx.Timeout(5.0, connect=2.0)) as client:
        r = client.get("/echo", params={"q": "tea"})
        print(r.status_code, r.json()["query"], r.http_version)
        r = client.get("/redirect")
        print(r.status_code, "-> not followed:", r.headers["location"])
        r = client.get("/redirect", follow_redirects=True)
        print(r.status_code, r.url.path)
        try:
            client.get("/status/500").raise_for_status()
        except httpx.HTTPStatusError as exc:
            print("HTTPStatusError", exc.response.status_code)

    async def fetch_all():
        async with httpx.AsyncClient(base_url=base, timeout=5) as client:
            replies = await asyncio.gather(*(client.get("/echo", params={"n": i}) for i in range(3)))
            return [r.json()["query"]["n"][0] for r in replies]

    print(asyncio.run(fetch_all()))
```
```text
200 {'q': ['tea']} HTTP/1.1
302 -> not followed: /final
200 /final
HTTPStatusError 500
['0', '1', '2']
```

- `httpx.Timeout(5.0, connect=2.0)` sets the default to 5 seconds and the connect timeout to 2. It really has four timeouts: **connect**, **read**, **write**, **pool** (waiting for a free connection in the pool).
- `r.http_version` shows `HTTP/1.1` here because our server speaks 1.1.
- The async example is the same call with `await`. Because the work is waiting for the network, three requests overlap (core.21).

### 19.2 Take the client as a parameter

The most useful design idea from core.21 repeats here. Write your API code so that the client is **passed in**:

```python
import httpx


def get_user_name(client: httpx.Client, user_id: int) -> str:
    response = client.get(f"/users/{user_id}")
    response.raise_for_status()
    return response.json()["name"]


def fake_server(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/users/1":
        return httpx.Response(200, json={"id": 1, "name": "Asha"})
    return httpx.Response(404, json={"error": "not found"})


with httpx.Client(transport=httpx.MockTransport(fake_server), base_url="https://api.example.com") as client:
    print(get_user_name(client, 1))
    try:
        get_user_name(client, 2)
    except httpx.HTTPStatusError as exc:
        print("failed:", exc.response.status_code)
```
```text
Asha
failed: 404
```

In production you pass `httpx.Client(base_url="https://api.example.com", timeout=...)`. In tests you pass the mock. Nothing else in the code changes, and no test ever touches the internet. (The URL above is only a label: the mock never sends it anywhere.)

## 20. Timeouts

### 20.1 The most important rule

> **Every network call must have a timeout.**

Section 2.3 said TCP never gives up by itself. If the server freezes, or a router drops your packets, your call waits for minutes or **for ever**. A thread that waits forever is a stuck worker; a hundred stuck workers is an outage. `requests.get(url)` without `timeout` has **no limit at all**. Let us prove it with a server that never answers (until we let it):

```python
import threading
import requests
from netlab import LabHandler, serve

release = threading.Event()


class Stuck(LabHandler):
    def do_GET(self):
        release.wait(10)                    # pretend the database froze
        self.reply(200, "finally\n")


with serve(Stuck) as base:
    result = []
    worker = threading.Thread(target=lambda: result.append(requests.get(base, timeout=None).status_code))
    worker.start()
    worker.join(0.5)
    print("after 0.5 s the client is still waiting:", worker.is_alive())
    release.set()                            # let the server answer
    worker.join(3)
    print("only then it finished:", result)
```
```text
after 0.5 s the client is still waiting: True
only then it finished: [200]
```

### 20.2 What can time out

```text
  client                                server
    |-- connect (handshake) ---------->|     connect timeout: the TCP handshake took too long
    |-- send the request ------------->|     write timeout: sending the body was too slow
    |   ... server is thinking ...     |
    |<-- first bytes of the response --|     read timeout: waited too long for the NEXT bytes
    |<-- more bytes -------------------|     (each wait gets its own timer)
```

- **Connect timeout**: the machine does not answer. Keep it **short** (2 to 5 seconds); a healthy server accepts in milliseconds.
- **Read timeout**: the server accepted but is slow. Choose from the API's normal speed: 5 to 30 seconds is typical. For a slow endpoint (report generation) allow more for that endpoint only.

With the three libraries:

```python
import socket
import threading

import httpx
import requests
from netlab import LabHandler, serve


class Slow(LabHandler):
    def do_GET(self):
        threading.Event().wait(0.6)          # takes 0.6 seconds to answer
        self.reply(200, "slow answer\n")


with serve(Slow) as base:
    host, port = "127.0.0.1", int(base.rsplit(":", 1)[1])
    with socket.create_connection((host, port), timeout=0.2) as s:           # raw socket
        s.sendall(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
        try:
            s.recv(100)
        except TimeoutError as exc:
            print("socket   :", type(exc).__name__)
    try:
        requests.get(base, timeout=(2, 0.2))                                  # (connect, read)
    except requests.ReadTimeout as exc:
        print("requests :", type(exc).__name__)
    try:
        httpx.get(base, timeout=httpx.Timeout(2, read=0.2))
    except httpx.ReadTimeout as exc:
        print("httpx    :", type(exc).__name__)

probe = socket.socket()
probe.bind(("127.0.0.1", 0))
closed_port = probe.getsockname()[1]
probe.close()
try:
    requests.get(f"http://127.0.0.1:{closed_port}", timeout=2)
except requests.ConnectionError as exc:
    print("requests, nobody home:", type(exc).__name__)
try:
    httpx.get(f"http://127.0.0.1:{closed_port}", timeout=2)
except httpx.ConnectError as exc:
    print("httpx, nobody home   :", type(exc).__name__)
```
```text
socket   : TimeoutError
requests : ReadTimeout
httpx    : ReadTimeout
requests, nobody home: ConnectionError
httpx, nobody home   : ConnectError
```

`requests` takes a tuple `(connect, read)`, `httpx` takes `httpx.Timeout(...)`. Note the **last two lines**: a closed port is not a timeout; it is an immediate refusal (section 5.3).

### 20.3 The trap: a timeout is per wait, not total

A read timeout restarts every time new bytes arrive. A server that dribbles one byte every second never trips a 5-second timeout and can keep you busy for hours. Here the server sends five pieces, 0.2 s apart (about 1 second in all), and the read timeout is only 0.5 s:

```python
import time
import requests
from netlab import LabHandler, serve


class Dribble(LabHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "5")
        self.end_headers()
        for _ in range(5):
            self.wfile.write(b".")
            self.wfile.flush()
            time.sleep(0.2)


def get_with_deadline(url, deadline_seconds, read_timeout):
    """Download url, but give up after deadline_seconds IN TOTAL."""
    started = time.monotonic()
    chunks = []
    with requests.get(url, stream=True, timeout=(2, read_timeout)) as r:
        for chunk in r.iter_content(chunk_size=1):
            chunks.append(chunk)
            if time.monotonic() - started > deadline_seconds:
                raise TimeoutError(f"gave up after {deadline_seconds} s with {len(chunks)} bytes")
    return b"".join(chunks)


with serve(Dribble) as base:
    began = time.monotonic()
    print(requests.get(base, timeout=0.5).content, "took more than 0.8 s:", time.monotonic() - began > 0.8)
    try:
        get_with_deadline(base, deadline_seconds=0.5, read_timeout=0.5)
    except TimeoutError as exc:
        print("total deadline:", "gave up" in str(exc))
```
```text
b'.....' took more than 0.8 s: True
total deadline: True
```

The first call succeeded although it took about a second: every single wait was under 0.5 s. A **total deadline** needs your own clock, as in `get_with_deadline`, or a wrapper such as `asyncio.timeout` in async code (core.21 section 12). For a whole *operation* with retries, also keep a total budget (section 22).

#### Try it on your machine: a connect timeout (needs a network)

A connect timeout needs an address that never answers. On many networks the "documentation" or unrouted ranges silently drop packets:

```text
$ python -c "import requests; requests.get('http://10.255.255.1', timeout=(2, 5))"
```

Expected on a network that drops the packets: after about 2 seconds a `requests.exceptions.ConnectTimeout`. On a network that rejects it instantly you see a `ConnectionError` ("Network is unreachable") at once instead. Which one you get, and the timings, are **machine-specific**.

## 21. Retries, backoff and jitter

### 21.1 Why retry, and why it can hurt

Networks fail briefly: a packet lost, a server restarting, a database failover taking 3 seconds. Retrying often turns a brief failure into a success. But retrying carelessly causes two kinds of damage:

1. **Duplicate actions.** A retried `POST /payments` may charge twice (section 9.3).
2. **Retry storms.** A server is overloaded; 10,000 clients all retry at once, every second; the extra load keeps it down.

So a good retry policy answers three questions: **Is it safe to repeat this request? How long do I wait? When do I give up?**

### 21.2 What is worth retrying

| Failure | Retry? | Reason |
|---|---|---|
| Connect refused / connect timeout / DNS failure | **yes, even for POST** | the request never reached the server |
| Read timeout, connection reset, short read | **only if the method is idempotent** | the server may have done the work |
| `408`, `429`, `500`, `502`, `503`, `504` | only if idempotent (`429` and `503` also if the server told you it did nothing) | transient |
| Other `4xx` (`400`, `401`, `403`, `404`, `422`) | **no** | your request is wrong; repeating cannot help |
| `2xx` / `3xx` | no | done |

### 21.3 Exponential backoff

Wait a little before the first retry, then twice as long, and so on: `delay = base * 2 ** attempt`, with a cap so that it does not grow forever. This gives a struggling server room to recover.

**Jitter** adds randomness. If a thousand clients fail at the same moment and all wait exactly 1, 2, 4 seconds, they all come back at the same moments in a herd. With *full jitter* each waits a **random** time between 0 and the current delay, which spreads the load.

```python
import random

BASE, CAP = 0.5, 8.0


def backoff_delay(attempt, rng):
    ceiling = min(CAP, BASE * 2 ** attempt)           # 0.5, 1, 2, 4, 8, 8, 8 ...
    return ceiling, rng.uniform(0, ceiling)           # full jitter: anywhere in [0, ceiling]


rng = random.Random(42)                               # a seeded generator, so this output repeats
print("attempt  ceiling  chosen wait")
for attempt in range(6):
    ceiling, wait = backoff_delay(attempt, rng)
    print(f"{attempt:>7}  {ceiling:>7}  {wait:>10.2f}")
```
```text
attempt  ceiling  chosen wait
      0      0.5        0.32
      1      1.0        0.03
      2      2.0        0.55
      3      4.0        0.89
      4      8.0        5.89
      5      8.0        5.41
```

The *ceiling* column is exact. The *chosen wait* column is random: with a different seed you see other numbers, always inside the ceiling. Seeding is only for tests and books; in production use the default random generator.

### 21.4 `Retry-After`

If the server tells you how long to wait (`429` or `503` with a `Retry-After` header), **believe it**: it knows better than your formula. The value is either a number of seconds or an HTTP date.

```python
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime


def retry_after_seconds(value, now):
    """Seconds to wait from a Retry-After header value, or None if unusable."""
    if value is None:
        return None
    if value.strip().isdigit():
        return int(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, (when - now).total_seconds())


now = datetime(2026, 11, 7, 10, 0, 0, tzinfo=timezone.utc)
later = format_datetime(datetime(2026, 11, 7, 10, 0, 30, tzinfo=timezone.utc), usegmt=True)
print(later)
for value in ("30", later, None, "soon", "0"):
    print(repr(value), "->", retry_after_seconds(value, now))
```
```text
Sat, 07 Nov 2026 10:00:30 GMT
'30' -> 30
'Sat, 07 Nov 2026 10:00:30 GMT' -> 30.0
None -> None
'soon' -> None
'0' -> 0
```

Always cap what you accept (a faulty server could say `Retry-After: 86400`), and tell the user or the logs rather than sleeping a day silently.

### 21.5 Idempotency keys: making POST safe to retry

How do payment APIs let you retry a `POST`? You generate a unique **idempotency key** for the logical operation and send it in a header (`Idempotency-Key: 7c1d...`). The server remembers the key and the result: a second request with the same key does **not** repeat the work; it returns the saved result. The key must be generated **once per operation** and reused unchanged for every retry.

```python
import json
import uuid
from netlab import LabHandler, call, serve


class Payments(LabHandler):
    charges = []                    # money actually taken
    saved = {}                      # idempotency key -> saved response

    def do_POST(self):
        key = self.headers.get("Idempotency-Key")
        if key and key in self.saved:
            return self.reply_json(200, self.saved[key], {"Idempotent-Replay": "true"})
        amount = json.loads(self.read_body())["amount"]
        self.charges.append(amount)
        result = {"charge_id": len(self.charges), "amount": amount}
        if key:
            self.saved[key] = result
        self.reply_json(201, result)


with serve(Payments) as base:
    for _ in range(2):                                           # blind retry, no key
        call(base, "POST", "/payments", {"amount": 500})
    print("without a key, two attempts took:", sum(Payments.charges))

    Payments.charges.clear()
    key = str(uuid.uuid4())                                       # ONE key for the operation
    for attempt in (1, 2, 3):
        status, headers, body = call(base, "POST", "/payments", {"amount": 500},
                                     headers={"Idempotency-Key": key})
        print("attempt", attempt, "->", status, body, headers.get("idempotent-replay"))
    print("with a key, the customer paid:", sum(Payments.charges))
```
```text
without a key, two attempts took: 1000
attempt 1 -> 201 {'charge_id': 1, 'amount': 500} None
attempt 2 -> 200 {'charge_id': 1, 'amount': 500} true
attempt 3 -> 200 {'charge_id': 1, 'amount': 500} true
with a key, the customer paid: 500
```

(A real server stores keys with an expiry and checks that a repeated key has the same body. The idea is the same.)

### 21.6 A circuit breaker, briefly

Retries help for short failures. If a server is down for ten minutes, every call spends its full timeout and retries, which wastes your resources and hammers the server. A **circuit breaker** notices repeated failures and **fails fast** for a while:

```text
   CLOSED (normal)  --N failures in a row-->  OPEN (reject immediately, no network)
        ^                                         |
        |  one trial call succeeds                | after a cool-down
        +------------- HALF-OPEN <----------------+
```

```python
class CircuitBreaker:
    def __init__(self, max_failures, cooldown, clock):
        self.max_failures, self.cooldown, self.clock = max_failures, cooldown, clock
        self.failures = 0
        self.opened_at = None

    def allow(self):
        if self.opened_at is None:
            return True                                    # closed
        if self.clock() - self.opened_at >= self.cooldown:
            return True                                    # half-open: let ONE call try
        return False                                       # open: fail fast

    def record(self, ok):
        if ok:
            self.failures, self.opened_at = 0, None
        else:
            self.failures += 1
            if self.failures >= self.max_failures:
                self.opened_at = self.clock()


now = [0.0]                                                # a fake clock we control
breaker = CircuitBreaker(max_failures=3, cooldown=10, clock=lambda: now[0])
for t, ok in [(0, False), (1, False), (2, False), (3, True), (13, True)]:
    now[0] = t
    allowed = breaker.allow()
    print(f"t={t:>2}  allowed={allowed!s:5}", end="")
    if allowed:
        breaker.record(ok)
        print(f"  call {'ok' if ok else 'FAILED'}", end="")
    print(f"  failures={breaker.failures}")
```
```text
t= 0  allowed=True   call FAILED  failures=1
t= 1  allowed=True   call FAILED  failures=2
t= 2  allowed=True   call FAILED  failures=3
t= 3  allowed=False  failures=3
t=13  allowed=True   call ok  failures=0
```

At `t=3` the circuit is open, so the call is not even tried. At `t=13` the cool-down is over, one trial call succeeds, and the circuit closes. Production libraries (`pybreaker`, service meshes) add more states and thread safety; the idea is only this. Passing the clock in makes it testable without waiting, the same trick we use for `sleep` in the next section.

#### Try it 21.1

Which of these may a client retry automatically after a **read timeout** (no response seen)? `GET /items`, `PUT /items/3`, `POST /orders`, `POST /orders` with an `Idempotency-Key`, `DELETE /items/3`.

<details><summary>Answer</summary>

All except the plain `POST /orders`. `GET`, `PUT` and `DELETE` are idempotent, so a duplicate changes nothing more. The keyed `POST` is made idempotent by the server's key store. The plain `POST` may have created the order already; a retry could create a second.
</details>

## 22. A resilient API client, step by step

We now combine sections 18 to 21 into one reusable class. We build it in four steps and then test it twice: fast and offline with `httpx.MockTransport`, and honestly against a local server that fails on purpose.

### 22.1 The design

- **Step 1, one attempt**: a client with a base URL, a default timeout, `raise_for_status` turned into our own `ApiError`.
- **Step 2, retry loop**: try up to `retries + 1` times for failures that are transient.
- **Step 3, wait wisely**: exponential backoff with full jitter, and `Retry-After` honoured (capped).
- **Step 4, safety**: only repeat requests that are safe to repeat: idempotent methods, or any method with an idempotency key; connection failures before sending are always safe.

Two design decisions make it testable: **`sleep` and `rng` are parameters** (tests pass a fake sleep that records instead of waiting, and a fixed random), and the **`httpx.Client` is a parameter** (tests pass one with a mock transport).

```python
"""resilient.py: an API client with timeouts, backoff, jitter and safe retries."""
import random
import time

import httpx

IDEMPOTENT_METHODS = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}
RETRY_STATUSES = {408, 429, 500, 502, 503, 504}
NEVER_SENT = (httpx.ConnectError, httpx.ConnectTimeout)      # the request did not reach the server


class ApiError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def retry_after(response, cap):
    value = response.headers.get("Retry-After", "")
    return min(float(value), cap) if value.strip().isdigit() else None


class ApiClient:
    def __init__(self, base_url, *, client=None, retries=3, backoff=0.2, cap=5.0,
                 timeout=httpx.Timeout(5.0, connect=2.0), sleep=time.sleep, rng=random.random):
        self.client = client or httpx.Client(base_url=base_url, timeout=timeout)
        self.retries, self.backoff, self.cap = retries, backoff, cap
        self.sleep, self.rng = sleep, rng
        self.retry_log = []                                  # (attempt, reason, wait) for each retry

    def _wait_for(self, attempt, response=None):
        if response is not None:
            told = retry_after(response, self.cap)
            if told is not None:
                return told                                  # the server knows best (capped)
        ceiling = min(self.cap, self.backoff * 2 ** (attempt - 1))
        return ceiling * self.rng()                          # full jitter

    def request(self, method, path, *, idempotency_key=None, **kwargs):
        method = method.upper()
        headers = dict(kwargs.pop("headers", None) or {})
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key     # the SAME key on every attempt
        repeatable = method in IDEMPOTENT_METHODS or bool(idempotency_key)
        for attempt in range(1, self.retries + 2):
            last = attempt == self.retries + 1
            try:
                response = self.client.request(method, path, headers=headers, **kwargs)
            except httpx.TransportError as exc:              # timeouts, refused, reset, ...
                safe = repeatable or isinstance(exc, NEVER_SENT)
                if last or not safe:
                    raise ApiError(f"{method} {path} failed: {type(exc).__name__}") from exc
                wait = self._wait_for(attempt)
                self.retry_log.append((attempt, type(exc).__name__, wait))
            else:
                if response.status_code in RETRY_STATUSES and repeatable and not last:
                    wait = self._wait_for(attempt, response)
                    self.retry_log.append((attempt, response.status_code, wait))
                elif response.status_code >= 400:
                    raise ApiError(f"{method} {path} -> {response.status_code}", response.status_code)
                else:
                    return response
            self.sleep(wait)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)
```

Walk through `request`:

1. We decide **once** whether the request is `repeatable` (step 4).
2. The loop runs at most `retries + 1` times. Each pass tries the call.
3. A `TransportError` (httpx's parent of timeouts, connection errors, resets) is retried only if it is safe; otherwise we raise our own `ApiError`, chaining the original with `from exc` (core.14) so the cause is not lost.
4. A response with a retryable status is retried if repeatable and attempts remain. Any other status of 400 or more raises `ApiError` right away (retrying a `404` is pointless). Success returns the response.
5. Before looping, `self.sleep(wait)` waits: the server's `Retry-After` if present (capped), else a jittered, doubling delay.
6. After the final failed attempt the error is raised: **retries are bounded**. An endless retry loop is just a hang with extra steps.

### 22.2 Test 1: fast and offline, with `MockTransport`

`script(...)` builds a fake server that answers with a prepared list of results, in order. A result can be a status code, a `(status, headers)` pair, or an exception to raise. The fake `sleep` records the waits instead of waiting, so the whole test runs in milliseconds. With `rng=lambda: 1.0` the jitter always picks the ceiling, so the waits are exact.

```python
import httpx
from resilient import ApiClient, ApiError


def make(*results):
    queue, calls, sleeps = list(results), [], []

    def handler(request):
        calls.append(request)
        result = queue.pop(0)
        if isinstance(result, Exception):
            raise result
        status, headers = result if isinstance(result, tuple) else (result, {})
        return httpx.Response(status, headers=headers, json={"status": status})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://api.test")
    api = ApiClient("http://api.test", client=client, sleep=sleeps.append, rng=lambda: 1.0)
    return api, calls, sleeps


def fails(api, method, path, **kw):
    """Run the call, expect ApiError, and return it."""
    try:
        api.request(method, path, **kw)
    except ApiError as exc:
        return exc
    raise AssertionError("expected ApiError")


def check(name, condition):
    print(("ok   " if condition else "FAIL ") + name)


api, calls, sleeps = make(503, 503, 200)
check("GET recovers after two 503s", api.get("/x").status_code == 200 and len(calls) == 3)
check("waits double: 0.2 then 0.4", sleeps == [0.2, 0.4])

api, calls, sleeps = make(503, 503, 503, 503)
exc = fails(api, "GET", "/x")
check("gives up after 1 + 3 attempts", len(calls) == 4 and sleeps == [0.2, 0.4, 0.8] and exc.status == 503)

api, calls, sleeps = make(404)
exc = fails(api, "GET", "/x")
check("404 is not retried", len(calls) == 1 and exc.status == 404 and sleeps == [])

api, calls, sleeps = make(503, 201)
exc = fails(api, "POST", "/orders", json={})
check("plain POST 503 is NOT retried", len(calls) == 1 and exc.status == 503)

api, calls, sleeps = make(503, 201)
r = api.post("/orders", json={}, idempotency_key="k-1")
check("POST with a key IS retried", r.status_code == 201 and len(calls) == 2)
check("same key on every attempt", {c.headers["Idempotency-Key"] for c in calls} == {"k-1"})

api, calls, sleeps = make(httpx.ConnectError("refused"), 201)
check("connect failure retried even for POST", api.post("/orders", json={}).status_code == 201)

api, calls, sleeps = make(httpx.ReadTimeout("slow"), 201)
exc = fails(api, "POST", "/orders", json={})
check("read timeout on plain POST not retried (maybe done!)", len(calls) == 1 and exc.status is None)

api, calls, sleeps = make((429, {"Retry-After": "2"}), (503, {"Retry-After": "999"}), 200)
api.get("/x")
check("Retry-After honoured, and capped at 5", sleeps == [2.0, 5.0])
```
```text
ok   GET recovers after two 503s
ok   waits double: 0.2 then 0.4
ok   gives up after 1 + 3 attempts
ok   404 is not retried
ok   plain POST 503 is NOT retried
ok   POST with a key IS retried
ok   same key on every attempt
ok   connect failure retried even for POST
ok   read timeout on plain POST not retried (maybe done!)
ok   Retry-After honoured, and capped at 5
```

Notice how each check states the **whole story**: the number of calls, the waits and the error. A test like `assert api.get("/x")` would pass for many wrong implementations. Strong assertions are what make a retry loop trustworthy, because its bugs (one attempt too many, a missing sleep) never crash; they only waste time or duplicate work.

### 22.3 Reading the retry log

The client also records each retry as `(attempt, reason, wait)`. That is the data you would put in your logs (core.17 `logging`) so that, when a user says "it was slow yesterday", you can see that the API returned `503` twice.

```python
import httpx
from resilient import ApiClient, ApiError

transport = httpx.MockTransport(lambda request: httpx.Response(503, json={}))
api = ApiClient("http://api.test", client=httpx.Client(transport=transport, base_url="http://api.test"),
                sleep=lambda s: None, rng=lambda: 1.0)
try:
    api.get("/x")
except ApiError as exc:
    print("error:", exc, "| status:", exc.status)
for entry in api.retry_log:
    print("retry log:", entry)
```
```text
error: GET /x -> 503 | status: 503
retry log: (1, 503, 0.2)
retry log: (2, 503, 0.4)
retry log: (3, 503, 0.8)
```

When a `GET` gives up, the last pass takes the "status 400 or more" branch and raises `ApiError("GET /x -> 503", 503)`: callers can read `.status` to see what the server finally said. And note: three waits for four attempts. There is no wait after the last attempt.

### 22.4 Test 2: a real server that fails on purpose

Mocks prove the logic. A real socket proves the plumbing: real timeouts, real dropped connections. This server fails the first N requests, either with `503` or by **closing the connection without answering**.

```python
import socket
import httpx
from netlab import LabHandler, serve
from resilient import ApiClient, ApiError


class Flaky(LabHandler):
    mode = "503"
    fail_first = 2
    seen = 0

    def do_GET(self):
        Flaky.seen += 1
        if Flaky.seen <= Flaky.fail_first:
            if Flaky.mode == "503":
                return self.reply_json(503, {"error": "busy"}, {"Retry-After": "1"})
            self.connection.shutdown(socket.SHUT_RDWR)       # hang up without a word
            self.close_connection = True
            return
        self.reply_json(200, {"attempt_that_worked": Flaky.seen})


def run(mode, fail_first, retries):
    Flaky.mode, Flaky.fail_first, Flaky.seen = mode, fail_first, 0
    waits = []
    with serve(Flaky) as base:
        api = ApiClient(base, retries=retries, sleep=waits.append, rng=lambda: 0.5)
        try:
            r = api.get("/data")
            return f"ok {r.json()} after {Flaky.seen} requests; log={[(a, w) for a, _, w in api.retry_log]}"
        except ApiError as exc:
            return f"gave up after {Flaky.seen} requests: {exc}"


print("503 twice, 3 retries   :", run("503", 2, 3))
print("hang-up twice, 3 retries:", run("drop", 2, 3))
print("503 forever, 2 retries :", run("503", 99, 2))
```
```text
503 twice, 3 retries   : ok {'attempt_that_worked': 3} after 3 requests; log=[(1, 1.0), (2, 1.0)]
hang-up twice, 3 retries: ok {'attempt_that_worked': 3} after 3 requests; log=[(1, 0.1), (2, 0.2)]
503 forever, 2 retries : gave up after 3 requests: GET /data -> 503
```

The real server did what the mock did: the client waited `Retry-After: 1` second (the fake `sleep` records instead of sleeping, so this ran instantly) in the first case; in the second case there is no header, so the jittered backoff is used (`0.2 * 0.5 = 0.1`, then `0.2`); and when the server never recovers, we stop after the allowed number of attempts. Mocks and real servers agreeing is exactly what you want from the two kinds of test.

### 22.5 The scary case: the reply that never arrived

This is the situation from section 1.1. The server **does the work, then drops the connection before replying.** Let us see what a naive retry does and what the idempotency key does.

```python
import socket
import uuid
from netlab import LabHandler, serve
from resilient import ApiClient, ApiError


class Payments(LabHandler):
    charges = []
    saved = {}
    drop_next_reply = True

    def do_POST(self):
        self.read_body()
        key = self.headers.get("Idempotency-Key")
        if key in self.saved:
            result = self.saved[key]                        # replay: no new charge
        else:
            self.charges.append(500)
            result = {"charge_id": len(self.charges)}
            if key:
                self.saved[key] = result
        if Payments.drop_next_reply:
            Payments.drop_next_reply = False
            self.connection.shutdown(socket.SHUT_RDWR)      # work done, reply lost
            self.close_connection = True
            return
        self.reply_json(201, result)


def attempt(label, **kw):
    Payments.charges.clear()
    Payments.saved.clear()
    Payments.drop_next_reply = True
    with serve(Payments) as base:
        api = ApiClient(base, sleep=lambda s: None)
        try:
            api.post("/payments", json={"amount": 500}, **kw)
            outcome = "success"
        except ApiError as exc:
            outcome = f"error ({type(exc.__cause__).__name__})"
    print(f"{label:34} outcome={outcome:32} customer charged {len(Payments.charges)} time(s)")


attempt("plain POST, client does not retry")
attempt("keyed POST, client retries", idempotency_key=str(uuid.uuid4()))
```
```text
plain POST, client does not retry  outcome=error (RemoteProtocolError)      customer charged 1 time(s)
keyed POST, client retries         outcome=success                          customer charged 1 time(s)
```

- **Plain POST**: the connection broke, the client does not retry (rule: not safe), raises `ApiError`. The customer **was charged once**, but our program says "error". The right response is *not* to blindly retry, but to check (`GET /payments?...`) or to use a key.
- **Keyed POST**: the client retried with the same key; the server found the saved result and did not charge again. One charge, one success. This is why serious APIs support idempotency keys, and why you generate the key **before** the first attempt.

(Had we retried the plain `POST` blindly, the customer would have been charged **twice**: the work was done once before the reply was lost, and the retry would do it again.)

#### Try it 22.1

Predict the waits recorded for a `GET` that gets `503` four times with `retries=3`, `backoff=0.2`, `cap=0.5` and `rng=lambda: 1.0`, no `Retry-After`.

```python
import httpx
from resilient import ApiClient, ApiError

waits = []
transport = httpx.MockTransport(lambda request: httpx.Response(503))
api = ApiClient("http://x.test", client=httpx.Client(transport=transport, base_url="http://x.test"),
                retries=3, backoff=0.2, cap=0.5, sleep=waits.append, rng=lambda: 1.0)
try:
    api.get("/")
except ApiError as exc:
    print(waits, exc.status)
```

<details><summary>Answer</summary>

```text
[0.2, 0.4, 0.5] 503
```

The ceilings are `0.2 * 2**0 = 0.2`, `0.2 * 2**1 = 0.4`, `0.2 * 2**2 = 0.8` but the cap is `0.5`, so the third is `0.5`. With `rng` always 1.0 each wait equals its ceiling: `[0.2, 0.4, 0.5]`. There are four attempts and three waits (no wait after the last). The final error carries status 503.
</details>


## 23. Web scraping with BeautifulSoup

### 23.1 What scraping is, and when not to do it

**Scraping** means fetching a web page and extracting data from its HTML. Use it only when no API exists. An API (section 14) gives you structured data, a stable contract and permission; a page's HTML is made for human eyes, and the designer may change it tomorrow without telling you. Ask first: *Is there an official API, a data download, an RSS feed?* Look at the browser's "Network" tab: many pages load their data from a hidden JSON API, which is much easier to use than the HTML.

HTML is a tree of **elements**: `<a href="/x" class="link">text</a>` has a tag name (`a`), attributes (`href`, `class`) and children (text or elements). **BeautifulSoup** (package `beautifulsoup4`, imported as `bs4`) parses HTML, even broken HTML, into a tree you can search.

### 23.2 Parsing and searching

We work on a small page in a string. No network is needed to learn the parsing.

```python
HTML = """
<html><head><title>Tea Shop - Catalog</title></head>
<body>
  <h1 id="shop-name">The Tea Shop</h1>
  <ul class="products">
    <li class="product" data-id="101"><a href="/tea/green">Green Tea</a> <span class="price">₹1,299</span></li>
    <li class="product sale" data-id="102"><a href="/tea/black">Black Tea</a> <span class="price">₹899</span></li>
    <li class="product" data-id="103"><a href="https://partner.example.org/chai">Masala Chai</a> <span class="price">₹450</span></li>
  </ul>
  <table id="stock">
    <tr><th>Item</th><th>Qty</th></tr>
    <tr><td>Green Tea</td><td>12</td></tr>
    <tr><td>Black Tea</td><td>0</td></tr>
  </table>
  <p class="note">Prices include tax.<br>Free delivery over &#8377;2,000.</p>
</body></html>
"""
```

```python
from bs4 import BeautifulSoup
from catalog_page import HTML

soup = BeautifulSoup(HTML, "html.parser")             # html.parser ships with Python: no extra install

print(soup.title.string)                              # first <title>
print(soup.find("h1")["id"], "|", soup.find(id="shop-name").get_text())

items = soup.find_all("li", class_="product")         # class_ because `class` is a Python keyword
print(len(items), [li["data-id"] for li in items])

for li in items:
    name = li.a.get_text(strip=True)                  # first <a> inside this <li>
    price = li.find("span", class_="price").get_text(strip=True)
    print(f"{name:12} {price:7} link={li.a['href']}")

print(soup.select("li.sale a")[0].get_text())         # CSS selector: <li class="sale"> then <a> inside
print(soup.select_one("ul.products > li:nth-of-type(3)")["data-id"])
print(soup.find("p", class_="note").get_text(" ", strip=True))
```
```text
Tea Shop - Catalog
shop-name | The Tea Shop
3 ['101', '102', '103']
Green Tea    ₹1,299  link=/tea/green
Black Tea    ₹899    link=/tea/black
Masala Chai  ₹450    link=https://partner.example.org/chai
Black Tea
103
Prices include tax. Free delivery over ₹2,000.
```

The methods you need:

| Call | Returns |
|---|---|
| `soup.find("tag", class_="x")` / `find(id="y")` | the **first** match, or `None` |
| `soup.find_all("tag", ...)` | a **list** of all matches (empty if none) |
| `soup.select("css selector")` / `select_one(...)` | list / first match, using CSS selectors (`ul.products > li`, `a[href^="https"]`) |
| `tag.get_text(strip=True)` | the text inside, with whitespace trimmed |
| `tag["href"]` / `tag.get("href")` | an attribute (`[]` raises `KeyError` if absent, `.get` gives `None`) |
| `tag.parent`, `tag.children`, `tag.next_sibling` | moving around the tree |

Two traps. **`find` returns `None` when nothing matches**, and then `.get_text()` raises `AttributeError: 'NoneType' object has no attribute...`. Real pages are inconsistent, so check for `None`. **`class` is a list**: an element with `class="product sale"` has `["product", "sale"]`, and `class_="product"` matches both words separately.

### 23.3 Cleaning the data

Scraped values are text. Convert them carefully, and handle absent data on purpose:

```python
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from catalog_page import HTML

soup = BeautifulSoup(HTML, "html.parser")
PAGE_URL = "http://shop.test/catalog/"


def parse_price(text):
    """'₹1,299' -> 1299 (int rupees). Return None if it is not a price."""
    digits = text.replace("₹", "").replace(",", "").strip()
    return int(digits) if digits.isdigit() else None


products = []
for li in soup.select("li.product"):
    link = li.find("a")
    price_tag = li.find("span", class_="price")
    products.append({
        "id": int(li["data-id"]),
        "name": link.get_text(strip=True),
        "url": urljoin(PAGE_URL, link["href"]),               # relative links -> absolute
        "price": parse_price(price_tag.get_text()) if price_tag else None,
        "on_sale": "sale" in li.get("class", []),
    })
for p in products:
    print(p)

# a table -> list of dicts
rows = soup.select("table#stock tr")
header = [th.get_text(strip=True) for th in rows[0].find_all("th")]
stock = [dict(zip(header, (td.get_text(strip=True) for td in tr.find_all("td")))) for tr in rows[1:]]
print(stock)
print(parse_price("free"), parse_price("₹ 2,000"))
```
```text
{'id': 101, 'name': 'Green Tea', 'url': 'http://shop.test/tea/green', 'price': 1299, 'on_sale': False}
{'id': 102, 'name': 'Black Tea', 'url': 'http://shop.test/tea/black', 'price': 899, 'on_sale': True}
{'id': 103, 'name': 'Masala Chai', 'url': 'https://partner.example.org/chai', 'price': 450, 'on_sale': False}
[{'Item': 'Green Tea', 'Qty': '12'}, {'Item': 'Black Tea', 'Qty': '0'}]
None 2000
```

`urljoin` (section 13) turns `/tea/green` into a full URL and leaves the already-absolute partner link alone. `zip(header, cells)` turns each table row into a dict.

### 23.4 Fetching then parsing

Put it together: a local "shop" serves the page; `requests` fetches it; BeautifulSoup extracts the data. The fetch and the parse are **separate functions**, so you can test the parser with a saved HTML string (fast, offline, deterministic) and never need the server in unit tests.

```python
import requests
from bs4 import BeautifulSoup
from catalog_page import HTML
from netlab import LabHandler, serve


def parse_catalog(html):
    soup = BeautifulSoup(html, "html.parser")
    return [(li["data-id"], li.a.get_text(strip=True)) for li in soup.select("li.product")]


def fetch_catalog(session, url):
    response = session.get(url, timeout=5)
    response.raise_for_status()
    return parse_catalog(response.text)


class Shop(LabHandler):
    def do_GET(self):
        if self.path == "/catalog/":
            self.reply(200, HTML, "text/html; charset=utf-8")
        else:
            self.reply(404, "not found\n")


print(parse_catalog(HTML))                               # test the parser without any network
with serve(Shop) as base, requests.Session() as session:
    print(fetch_catalog(session, base + "/catalog/"))
    try:
        fetch_catalog(session, base + "/missing/")
    except requests.HTTPError as exc:
        print("page gone:", exc.response.status_code)
```
```text
[('101', 'Green Tea'), ('102', 'Black Tea'), ('103', 'Masala Chai')]
[('101', 'Green Tea'), ('102', 'Black Tea'), ('103', 'Masala Chai')]
page gone: 404
```

Further cautions:

- **JavaScript-built pages.** `requests` receives the HTML the server sent, *before* any JavaScript runs. If the data appears only in the browser, it is not in your `response.text`. Look for the JSON API behind the page, or use a browser-automation tool (Playwright, Selenium), which is a separate and heavier topic.
- **Encoding.** Use `response.text` for HTML; `requests` guesses the charset from the headers. If you see `Ã©` instead of `é`, set `response.encoding = "utf-8"`.
- **Layout changes break scrapers.** Prefer stable hooks (`id`, `data-` attributes) over fragile ones (`div > div:nth-child(4)`), validate what you extracted (is the price a number?), and **fail loudly** when the page no longer has the shape you expect.

#### Try it 23.1

Predict the output. (Remember what `find` returns when nothing matches, and that `find_all` returns a list.)

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup("<div><p class='a b'>one</p><p>two</p></div>", "html.parser")
print(soup.find("span"))
print(len(soup.find_all("p")), len(soup.find_all("p", class_="b")), soup.find("p")["class"])
print(soup.find("p", class_="zzz") is None, soup.select_one("div > p:nth-of-type(2)").text)
```

<details><summary>Answer</summary>

```text
None
2 1 ['a', 'b']
True two
```

`find("span")` prints `None` (no span exists). There are 2 paragraphs, 1 with class `b`, and the first paragraph's `class` is the list `['a', 'b']`. The missing class gives `None` (so `True`), and the CSS selector finds the second `p`, whose text is `two`. Never write `soup.find("span").text` without checking for `None` first.
</details>

## 24. Being a polite scraper

### 24.1 Rules of the road

A scraper is a guest in someone else's house. Servers cost money, and a careless crawler can slow or crash a small site. The rules:

1. **Check for an API or a data export first.**
2. **Read the terms of service.** Some sites forbid scraping. Respect them; ignoring them can have legal consequences, and the law differs from country to country.
3. **Read `robots.txt`** (`https://site/robots.txt`). It states which paths automated clients may fetch, and sometimes a `Crawl-delay`. It is not a security tool (it is a request), but honouring it is the minimum standard of conduct.
4. **Identify yourself**: set a clear `User-Agent` with a contact (`my-course-bot/1.0 (asha@example.com)`), not a fake browser name.
5. **Limit your rate.** One request per second or slower for a small site. Fetch each page once; cache what you have.
6. **Back off when asked.** On `429` or `503` obey `Retry-After` (section 21). Stop on repeated `403`.
7. **Do not collect personal data** you have no right to, and do not republish copyrighted content.
8. **Use conditional requests** (`ETag`, section 11.5) for pages you poll.

### 24.2 `robots.txt` with the standard library

```python
from urllib.robotparser import RobotFileParser

ROBOTS = """
User-agent: *
Disallow: /private/
Disallow: /search
Crawl-delay: 2

User-agent: badbot
Disallow: /
""".strip().splitlines()

rp = RobotFileParser()
rp.parse(ROBOTS)                                       # with a real site: rp.set_url(url); rp.read()
for agent, url in [("my-course-bot", "http://shop.test/tea/green"),
                   ("my-course-bot", "http://shop.test/private/orders"),
                   ("my-course-bot", "http://shop.test/search?q=tea"),
                   ("badbot", "http://shop.test/tea/green")]:
    print(f"{agent:14} {url:34} allowed={rp.can_fetch(agent, url)}")
print("crawl delay:", rp.crawl_delay("my-course-bot"))
```
```text
my-course-bot  http://shop.test/tea/green         allowed=True
my-course-bot  http://shop.test/private/orders    allowed=False
my-course-bot  http://shop.test/search?q=tea      allowed=False
badbot         http://shop.test/tea/green         allowed=False
crawl delay: 2
```

With a real site you call `rp.set_url("https://site/robots.txt")` then `rp.read()` (this needs the internet) and ask `can_fetch` before every URL.

### 24.3 A rate limiter you can test

Waiting between requests is a small piece of code. As in section 22, we inject the clock and `sleep` so that the test does not really wait:

```python
class RateLimiter:
    """Allow at most one call every `interval` seconds."""

    def __init__(self, interval, clock, sleep):
        self.interval, self.clock, self.sleep = interval, clock, sleep
        self.last = None

    def wait(self):
        now = self.clock()
        if self.last is not None:
            remaining = self.interval - (now - self.last)
            if remaining > 0:
                self.sleep(remaining)
                now = self.clock()
        self.last = now


fake_time = [0.0]
waits = []


def fake_sleep(seconds):
    waits.append(round(seconds, 2))
    fake_time[0] += seconds                        # sleeping advances the fake clock


limiter = RateLimiter(2.0, clock=lambda: fake_time[0], sleep=fake_sleep)
for step in (0.0, 0.5, 5.0):                       # our "work" takes this long between requests
    limiter.wait()
    fake_time[0] += step
print("waits before each request:", waits)
```
```text
waits before each request: [2.0, 1.5]
```

The first request goes at once. Its work took 0.0 s, so the second request must wait the full 2.0 s. The second request's work took 0.5 s, so the third waits only the remaining 1.5 s. Had the work taken 5 s, the next call would not wait at all. That is the point of sleeping for the *remaining* time instead of a fixed sleep.

## 25. What happens when you type a URL

This section ties the chapter together. You type `https://shop.example.com/tea?id=7` and press Enter. What happens?

```text
  1. PARSE      browser splits the URL: scheme https, host shop.example.com, port 443 (default),
                path /tea, query id=7                                         (section 13)
  2. CACHE      is there a fresh copy (Cache-Control / ETag)? If yes, maybe no request at all  (11.5)
  3. DNS        shop.example.com -> 203.0.113.7 (cache, resolver, root, .com, ...)           (section 4)
  4. TCP        three-way handshake to 203.0.113.7:443            (1 round trip)           (5.3)
  5. TLS        hello, certificate checked (chain, name, dates), keys agreed (1 round trip) (section 17)
  6. REQUEST    "GET /tea?id=7 HTTP/1.1", Host, cookies, Accept, User-Agent                (7, 8, 12)
  7. SERVER     load balancer -> web server -> app code -> database ... builds the answer  (15, 16)
  8. RESPONSE   "200 OK", headers, body (HTML), framed by Content-Length / chunked          (6, 8.4)
  9. RENDER     browser parses HTML; for each CSS/JS/image repeat steps 2-8 (often on the
                SAME connection, thanks to keep-alive / HTTP/2)                            (15.4)
 10. CLOSE      the connection stays idle for reuse, then closes (FIN)
```

Where does the time go? On a typical long-distance connection, steps 3 to 5 cost several **round trips** before your request is even sent. These are illustrative figures, not measurements:

```text
  Step              Round trips   at 50 ms per round trip
  DNS (uncached)        1-2             50-100 ms
  TCP handshake         1                    50 ms
  TLS 1.3 handshake     1                    50 ms
  HTTP request/reply    1                    50 ms + server time
```

That is why caching DNS, reusing connections, and fewer, bigger requests matter. And it tells you where it can **fail**, which is the best debugging map in this course:

| Symptom | Which step | Typical cause |
|---|---|---|
| "could not resolve host" / `gaierror` | 3 DNS | typo, DNS server down, no network |
| "connection refused" | 4 TCP | server program not running, wrong port |
| hangs, then connect timeout | 4 TCP | firewall drops packets, server machine down |
| certificate errors | 5 TLS | wrong name, expired, unknown CA, wrong clock |
| `400`, `404`, `405`, `401`, `403` | 6/7 | the request is wrong or not allowed |
| `500`, `502`, `503`, `504` | 7 | server bug, overloaded, upstream down |
| read timeout | 7/8 | slow server, no timeout set |
| half a page, wrong characters | 8 | bad `Content-Length` or `Content-Type`/charset |

### 25.1 A mini browser: every step in code

We can now write the client side of steps 1 to 8 ourselves, with only `urllib.parse` and `socket`. It handles `http` (for `https` you would wrap the socket as in section 17.4, then continue identically). Save it as `minifetch.py`.

```python
"""minifetch.py: fetch a URL step by step with only urllib.parse and socket (http only)."""
import socket
from urllib.parse import urlsplit


def mini_fetch(url, trace=print, timeout=5):
    # 1. PARSE
    parts = urlsplit(url)
    if parts.scheme != "http":
        raise ValueError("this mini client only speaks http")
    host, port = parts.hostname, parts.port or 80
    target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    trace(f"1. parse: host={host} path={target}")

    # 2/3. DNS: ask the resolver for an address
    family, kind, proto, _, address = socket.getaddrinfo(host, port, family=socket.AF_INET,
                                                         type=socket.SOCK_STREAM)[0]
    trace(f"3. dns: {host} -> {address[0]}")

    # 4. TCP: connect (the three-way handshake happens here)
    with socket.create_connection(address, timeout=timeout) as sock:
        trace("4. tcp: connected")

        # 6. REQUEST: just text
        request = f"GET {target} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: minifetch/1.0\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode("ascii"))
        trace(f"6. request: sent {len(request)} bytes")

        # 8. RESPONSE: read until the headers end, then the body
        with sock.makefile("rb") as reader:
            status_line = reader.readline().decode("latin-1").rstrip("\r\n")
            headers = {}
            while (line := reader.readline()) not in (b"\r\n", b""):
                name, _, value = line.decode("latin-1").partition(":")
                headers[name.strip().lower()] = value.strip()
            length = headers.get("content-length")
            body = reader.read(int(length)) if length is not None else reader.read()
    status = int(status_line.split(" ")[1])
    trace(f"8. response: {status_line!r}, {len(body)} body bytes (Content-Length={length})")
    return status, headers, body
```

And we test it against our own raw-socket server from section 15, so no standard library HTTP code is involved on either side:

```python
from minifetch import mini_fetch
from tinyhttp import TinyServer


def page(request):
    return 200, f"<h1>Tea</h1> id={request.query.get('id', ['?'])[0]}\n"


with TinyServer({"/tea": {"GET": page}}) as server:
    status, headers, body = mini_fetch(server.base.replace("127.0.0.1", "localhost") + "/tea?id=7")
    print(status, body.decode().strip())
    print(headers["content-type"])
    status, _, body = mini_fetch(server.base + "/missing")
    print(status, body.decode().strip())
```
```text
1. parse: host=localhost path=/tea?id=7
3. dns: localhost -> 127.0.0.1
4. tcp: connected
6. request: sent 89 bytes
8. response: 'HTTP/1.1 200 OK', 18 body bytes (Content-Length=18)
200 <h1>Tea</h1> id=7
text/plain; charset=utf-8
1. parse: host=127.0.0.1 path=/missing
3. dns: 127.0.0.1 -> 127.0.0.1
4. tcp: connected
6. request: sent 88 bytes
8. response: 'HTTP/1.1 404 Not Found', 13 body bytes (Content-Length=13)
404 no such path
```

Our own client talking to our own server, written in about 190 lines in total, with every step of the journey visible. Notice that we typed `localhost` in the first URL, so step 3 really resolved a name (to `127.0.0.1`), the DNS part from section 4.

## 26. Project: a raw-socket server and a resilient client

**Goal.** Build the two halves of an HTTP conversation and show they hold up under failure.

### Part 1: `notes_server.py`, a raw-socket HTTP server

Use `tinyhttp.py` (or write your own from scratch: that is the point) to serve a small notes API on `127.0.0.1` and a **free port** (port 0):

| Route | Behaviour |
|---|---|
| `GET /notes` | `200` + JSON list; supports `?limit=` and `?offset=`; invalid numbers give `400` with a JSON error |
| `POST /notes` | JSON `{"text": "..."}`; `201` + `Location`; `422` if `text` is missing or empty |
| `GET /notes/<id>` | `200` or `404` |
| `PUT /notes/<id>` | replace; `200`, or `404` |
| `DELETE /notes/<id>` | `204`, or `404` |
| any other method | `405` with `Allow` |

Requirements: correct `Content-Length` (test with non-ASCII text), keep-alive on HTTP/1.1 and `Connection: close` honoured, a limit on header and body sizes, a `500` JSON error for a handler that crashes (the server keeps running), and a `POST` that supports an `Idempotency-Key`.

### Part 2: `notes_client.py`, a resilient client

Using `resilient.py` as the starting point, write a `NotesClient` with `list_all()` (follows pagination), `add(text)` (uses an idempotency key), `get(id)`, `delete(id)`. Requirements: timeouts everywhere; retries only where safe; a total time budget for one operation; useful `ApiError` messages; the client takes an `httpx.Client` so it can be tested.

### Part 3: prove it

1. Tests against `httpx.MockTransport`, with a fake `sleep`: success, retry on `503`, give up, `Retry-After`, no retry of plain `POST`, retry of keyed `POST`.
2. Integration tests against a flaky wrapper around your own server: drop the first N connections, return `503` for the first N requests, answer slowly (read timeout), and drop the reply **after** doing the work (check that the keyed `POST` creates exactly one note).
3. A script `demo.py` that starts the server on a free port, runs the client through a list of notes, and prints a short report.

**Done when** all tests pass without touching the internet, no port is hard-coded, the server survives a malformed request, and the report shows exactly one note per logical `add`.

**Stretch goals.** Add `ETag` / `If-None-Match` to `GET /notes/<id>`; wrap the socket in TLS with the certificate helper of section 17.4; add a circuit breaker to the client; make an async version with `httpx.AsyncClient`.

## 27. Common traps

Collected from the whole chapter. Read them before a real project.

**Sockets and framing**
1. **Assuming one `send` equals one `recv`.** TCP is a byte stream; frame your messages (section 6).
2. **Ignoring `recv()` returning `b""`.** It means the peer closed; an unchecked loop spins forever.
3. **Using `send` instead of `sendall`**, silently sending only part of the data.
4. **Sending `str` instead of `bytes`**, or measuring `len(text)` instead of `len(text.encode())`.
5. **Hard-coding a port.** Use port 0 in tests; handle `Address already in use` in real servers.
6. **Binding to `0.0.0.0` for development**, exposing an unfinished server to your whole network.
7. **`localhost` vs `127.0.0.1`** resolving to different families (IPv6 `::1` against IPv4).

**HTTP**
8. **Wrong `Content-Length`** (characters instead of bytes): the client truncates or hangs.
9. **A `GET` that changes data.** Crawlers, prefetchers and retries will call it.
10. **Retrying a non-idempotent request** (`POST`) after a timeout, without an idempotency key.
11. **Mixing `json=` and `data=`** in `requests`; wrong `Content-Type` gives `415` or `422`.
12. **Treating `401` and `403` as the same**, or answering `200` with an error inside the JSON.
13. **Building URLs with f-strings** and unescaped user input; use `params=` and `urlencode`/`quote`.
14. **Ignoring the body of an error response.** It usually says what is wrong.
15. **Putting tokens in URLs, logs or error messages.**
16. **Calling `.json()` on a `204` or on an HTML error page.**

**Clients and failure**
17. **No timeout.** `requests` waits forever by default. Always pass `timeout=`.
18. **Believing a read timeout is a total deadline.** It restarts with every byte.
19. **Retrying without a limit, without backoff, or without jitter.** That is a self-made attack on the server.
20. **Retrying `4xx` errors.** `400`, `404`, `422` will fail again.
21. **Ignoring `Retry-After`**, or obeying a huge one without a cap.
22. **Creating a new `Session`/`Client` for every request.** You lose connection reuse. Create one and close it with `with`.
23. **`verify=False` to "fix" a certificate error.** Fix the trust or the name instead.
24. **Not closing responses** when streaming (`with requests.get(..., stream=True)`).
25. **Tests that hit the real internet**: slow, flaky, and a hidden dependency. Use `MockTransport` or a local server.
26. **Passing `sleep`/`clock`-using code without injection**, making retry tests slow or timing-dependent.
27. **Tests with weak assertions** that cannot fail (`and`/`or` mixed up, or only checking "no exception").

**Scraping**
28. **`find(...)` returning `None`** and then `.text` crashing.
29. **Scraping when an API exists**, or ignoring `robots.txt`, terms of service and rate limits.
30. **Parsing the browser's page instead of the server's HTML.** JavaScript-built content is not in `response.text`.
31. **Fragile selectors** (`div > div:nth-child(4)`) that break on a redesign, and scrapers that fail silently.

## 28. Summary

- Networks are layered: **link, internet (IP), transport (TCP/UDP), application (HTTP)**. IP finds a computer, a **port** finds a program, **DNS** turns names into addresses. `127.0.0.1` is "this computer"; port 0 means "pick a free port".
- **TCP** gives a reliable, ordered **byte stream** with **no message boundaries**: frame your messages with a delimiter, a length prefix, or by closing. `recv()` returning `b""` means the peer closed. Use `sendall`. UDP keeps message boundaries but promises no delivery.
- **HTTP is text on a TCP stream**: a request line, headers, a blank line and an optional body; a status line, headers and a body. Body length comes from `Content-Length` (counted in **bytes**), `chunked`, or closing. HTTP/1.1 connections are **kept alive**, which saves handshakes.
- **Methods** have meaning: `GET` is safe; `GET`, `PUT`, `DELETE` are idempotent; `POST` is neither. **Status families**: 2xx success, 3xx redirect, 4xx your fault, 5xx their fault. Know `200 201 204 301 304 400 401 403 404 405 409 422 429 500 503`. Headers carry the metadata: `Content-Type`, `Accept`, `Authorization`, `Cache-Control`, `ETag`, `Location`, `Retry-After`.
- **Cookies** give a stateless protocol memory (`Set-Cookie`, `Cookie`); a **session** is the server-side data behind a cookie. Use `HttpOnly`, `Secure`, `SameSite`.
- **REST/JSON APIs** use nouns in URLs, methods as verbs, status codes for results, pagination, a consistent error shape, and versions. Flask or Django do the plumbing that our 150-line raw server did by hand.
- **HTTPS = HTTP over TLS**: encryption, integrity and authentication through a certificate that must lead to a trusted CA and match the host name. Never switch verification off.
- **`requests`** (sync, no default timeout) and **`httpx`** (sync and async, 5 s default, `MockTransport`): reuse a `Session`/`Client`, pass `timeout`, call `raise_for_status()`, and pass the client into your functions so tests can fake the server.
- **Every call needs a timeout**: connect (short), read (per wait, not total). Add your own total deadline.
- **Retry only what is safe**: connection failures always; idempotent methods on timeouts and `408/429/500/502/503/504`; `POST` only with an **idempotency key**. Wait with **exponential backoff and jitter**, honour a capped `Retry-After`, bound the attempts, and consider a circuit breaker.
- **Test the failures** against `MockTransport` and a local flaky server, with `sleep` and the random source injected.
- **Scraping** is the last resort after an API: parse with BeautifulSoup (`find`, `find_all`, `select`, check for `None`), separate fetching from parsing, read `robots.txt`, identify yourself, and rate-limit.
- When you type a URL: **parse, cache, DNS, TCP, TLS, request, server work, response, render**. Each step has its own failures, and you now know how to recognise and handle them.

Next in the course you will use this to build and consume real services, with the habits from swe.01 (tests, tooling, documentation) around them.
