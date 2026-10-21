# Split an email address

Read an email address (it contains exactly one `@`, and the part before it has at least one character). Spaces at the ends should be ignored. Print:

```
User: <the part before @, unchanged>
Domain: <the part after @, in lowercase>
Masked: <first character of the user>***@<lowercase domain>
```

**Example**

Input:
```
  Asha.Kumar@Example.COM
```
Output:
```
User: Asha.Kumar
Domain: example.com
Masked: A***@example.com
```

Domains are not case-sensitive, so they are shown in lowercase. The user part can be case-sensitive, so it is kept as typed.
