# One number, many bases

Read a non-negative whole number. Print:

```
bin: <binary>
oct: <octal>
hex: <hex, lowercase>
prefixed: <binary with 0b> <octal with 0o> <hex with 0x>
byte: <binary padded with zeros to at least 8 digits>
grouped: <binary with _ every 4 digits>
```

**Example**

Input:
```
202
```
Output:
```
bin: 11001010
oct: 312
hex: ca
prefixed: 0b11001010 0o312 0xca
byte: 11001010
grouped: 1100_1010
```
