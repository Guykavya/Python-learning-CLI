# title() versus capwords()

Book titles typed by users need fixing. Read a line and print three versions:

```
title: <text.title()>
capwords: <string.capwords(text)>
capitalize: <text.capitalize()>
```

**Example**

Input:
```
they're   ROCK'N'ROLL fans
```
Output:
```
title: They'Re   Rock'N'Roll Fans
capwords: They're Rock'n'roll Fans
capitalize: They're   rock'n'roll fans
```

Then look at the output and make sure you can explain each difference: which ones collapse spaces, and how each treats apostrophes.
