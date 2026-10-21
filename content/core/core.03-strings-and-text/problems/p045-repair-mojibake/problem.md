# Repair mojibake

A program saved names in UTF-8, but another program read them back as latin-1. Now the data is full of mojibake like `cafÃ©`. Read one garbled line and repair it by reversing the mistake. Print:

```
Fixed: <the repaired text>
Shorter by: <how many characters shorter the fixed text is>
```

**Example**

Input:
```
naÃ¯ve rÃ©sumÃ©
```
Output:
```
Fixed: naïve résumé
Shorter by: 3
```

Plain ASCII lines contain no mojibake and come back unchanged.
