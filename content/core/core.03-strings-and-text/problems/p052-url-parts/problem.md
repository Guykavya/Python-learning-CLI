# Take apart a URL

Read a web address of this shape (only the scheme and host are always present):

```
scheme://host[:port][/path][?query][#fragment]
```

Print:

```
Scheme: <scheme, lowercase>
Host: <host, lowercase>
Port: <port, or (default)>
Path: <path starting with /, or just / if there is none>
Query: <query, or (none)>
Fragment: <fragment, or (none)>
```

**Example**

Input:
```
HTTPS://Example.COM:8080/docs/page.html?lang=en&q=str#top
```
Output:
```
Scheme: https
Host: example.com
Port: 8080
Path: /docs/page.html
Query: lang=en&q=str
Fragment: top
```

Hint: peel the URL from the outside in. The fragment comes after the first `#`, the query after the first `?`, and so on. Use `partition` at each step, and `or` for the defaults.
