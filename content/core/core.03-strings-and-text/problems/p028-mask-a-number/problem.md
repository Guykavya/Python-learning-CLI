# Mask a card number

Read a card or phone number that may contain spaces and dashes. Print:

```
Digits: <how many characters remain after removing spaces and dashes>
Masked: <all but the last 4 replaced by *>
```

**Example**

Input:
```
4111-1111 1111-1234
```
Output:
```
Digits: 16
Masked: ************1234
```

If there are 4 or fewer characters, nothing is masked.
