# Phone lookup

Read `n`, then `n` lines of `name number`. Then read `m`, then `m` names to look up.
For each name print its number, or `Not found: <name>` if the name is unknown.

If the same name appears twice in the first part, the **later** number replaces the earlier one.
Names are case-sensitive.

**Example**

Input:
```
3
Asha 98200
Ravi 98111
Asha 90000
3
Asha
Meena
Ravi
```
Output:
```
90000
Not found: Meena
98111
```
