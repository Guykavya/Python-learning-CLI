# File permission bits

On Linux, a file's permissions for one user are stored in 3 bits: read = 4, write = 2, execute = 1.
A mode is their sum, a number from 0 to 7. For example, 6 means read and write.

Read a mode (0 to 7). Print:

```
Binary: <the mode with bin()>
Read: <True/False>
Write: <True/False>
Execute: <True/False>
Without write: <the mode with the write bit turned off>
With execute: <the mode with the execute bit turned on>
```

Use bitwise operators `&`, `|` and `~`.

**Example**

Input:
```
6
```
Output:
```
Binary: 0b110
Read: True
Write: True
Execute: False
Without write: 4
With execute: 7
```
