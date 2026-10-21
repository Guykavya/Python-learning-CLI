# Two clubs

Read two lines of member names: the first line is the Python club, the second is the Chess
club. Either line may be empty, and a name may be repeated by mistake (count it once).

Print four lines. In each line, list the names **sorted** and separated by spaces, or `-` if
there are none:

```
Both: <in both clubs>
Only Python: <in Python but not Chess>
Only Chess: <in Chess but not Python>
Either: <in at least one club>
```

**Example**

Input:
```
asha ravi meena kiran
ravi kiran john ravi
```
Output:
```
Both: kiran ravi
Only Python: asha meena
Only Chess: john
Either: asha john kiran meena ravi
```
