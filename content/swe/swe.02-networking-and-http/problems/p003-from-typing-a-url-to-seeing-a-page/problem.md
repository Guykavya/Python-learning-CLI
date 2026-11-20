# From typing a URL to seeing a page

You type `https://shop.example/books?page=2#top` into a browser and press Enter. A page appears. Chapter section 25 follows the whole journey.

In `answer.md`, explain the journey **in order**, in your own words (12 to 20 sentences or a numbered list). For **each step** name:

- what happens,
- which layer or protocol does it (IP, DNS, TCP, TLS, HTTP),
- **one thing that can fail** at that step and what the user then sees.

Cover at least these steps: (1) parsing the URL, (2) finding the address, (3) opening the connection, (4) making it secure, (5) sending the request, (6) the response, (7) reusing the connection, (8) what the browser does with the page, (9) what it does with the `#top` part, (10) closing or keeping the connection.

Also say which parts of this journey **an eavesdropper on the same Wi-Fi can still see** even with HTTPS.
