## Hint 1

For each snippet ask: *what does this code need to happen, and when?* Does it need to run
code once when a subclass is created? To compute a value when an attribute is read? To generate
standard methods from a list of fields? Then pick the smallest tool that runs at that moment.
For the costs, imagine three people: a reader who opens the file, an IDE that wants to
autocomplete `p.`, and a user who makes a typo.

## Hint 2

```
A: generates __init__/__repr__/__eq__ from field names      -> @dataclass
   costs: tools can't see fields; wrong argument counts pass silently (zip); __hash__ lost; must maintain it
B: computes two derived values on read                        -> one @property each
   costs: invisible to dir()/IDE; growing if-chain
   bug:   'return None' for every other name (typos, hasattr, copy/pickle)
C: runs once per subclass: check + register                   -> __init_subclass__ (or a class decorator)
   costs: metaclass conflicts with ABC etc.; the 'if bases:' trick
justified metaclass: operations ON the class (len, iteration, Color(2), blocking Color.X = ...) or __prepare__
```
