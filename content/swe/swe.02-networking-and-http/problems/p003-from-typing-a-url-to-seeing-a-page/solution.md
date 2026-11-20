## Approach

The model answer is in `answer.md`. The skeleton to memorise: **URL → DNS → TCP → TLS → HTTP → render**, and for each arrow, the question "what if this step fails?".

Practise it with chapter section 25.1: the `mini_fetch` function does steps 1, 3, 4, 6 and 8 in about 40 lines, printing a line for each.

## Complexity

Not applicable.

## Another way

Draw it as a sequence diagram with three lanes (browser, DNS server, web server) and number every arrow. If you can redraw it from memory, you know it.

## Why it matters

When a page does not load, the layer where it fails tells you where to look: DNS (name), TCP (port, firewall), TLS (certificate, clock), HTTP (status code). Debugging by layer is the whole skill.
