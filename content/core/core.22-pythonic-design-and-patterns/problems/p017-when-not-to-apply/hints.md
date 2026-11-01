## Hint 1

For each snippet ask: *what changes from one use to the next?* If nothing changes, what is the
class protecting? Then ask: which Python feature (function, dict, module, duck typing) already
does that job?

## Hint 2

Use this skeleton for every part, one or two sentences each:

```
X. Claims to solve: ...
   Python does not need it because: ... (function / module / dict / Protocol)
   Simple version: ...code...
   Worth it when: ... (many implementations, shared state, families, real exclusivity)
```

Keep the "worth it" situation concrete (a plugin system, a UI toolkit, a hardware port), not
"when the project is big".
