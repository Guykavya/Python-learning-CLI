## Hint 1

Start with `base.html` alone: each block prints its default content, on its own line. Then ask which blocks a child **replaces** and which it leaves alone.

## Hint 2

`super()` renders the block of the **parent** template (one level up), then you add your own text around it. In a grandchild, the parent is `page.html`, whose `content` block itself replaced the one in `base.html`. Variables from `render(...)` are visible in every template of the chain.

## Hint 3

```text
base.html     head / content / footer as written
page.html     head = "[page head] " + super() (= base head); content replaced; footer from base
special.html  head from page; content = "[special] " + super() (= page's content); footer replaced by DEMO
```
