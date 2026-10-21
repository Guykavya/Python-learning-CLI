# IPv4 addresses as integers

An IPv4 address like `192.168.1.1` is really one 32-bit number: the four parts (octets, each 0-255)
are its four bytes, highest first.

Read **five** lines: the four octets of an address (one per line), then a whole number `x`
between 0 and 4294967295. Print:

```
Integer: <the address as one 32-bit number>
Hex: <that number with hex()>
Address: <x written as four octets separated by dots>
```

Use shifts (`<<`, `>>`), `|` and `&`. Arithmetic with `* 256` also works, but practise the bit operators.

**Example**

Input:
```
192
168
1
1
167772161
```
Output:
```
Integer: 3232235777
Hex: 0xc0a80101
Address: 10.0.0.1
```
