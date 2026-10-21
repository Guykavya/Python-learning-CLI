# Format a name for a register

A class register needs names as `Surname, Firstname` plus initials. People type names carelessly.

Read one line containing a full name: at least two words, possibly with extra spaces and random capitals. The **first word** is the first name and the **last word** is the surname (middle names are ignored). Print:

```
<Surname>, <Firstname>
Initials: <F>.<S>.
```

Each name is shown with its first letter uppercase and the rest lowercase (use `capitalize()`).

**Example**

Input:
```
   aDA   byron  LOVELACE
```
Output:
```
Lovelace, Ada
Initials: A.L.
```
