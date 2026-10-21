# Contact book

Build an in-memory **contact book** driven by typed commands. This is the module project in
assessed form. Read commands until `quit`, then print `Goodbye`.

Every contact has a NAME (one word, case-sensitive) and a PHONE (one word of digits). No two
contacts may share a phone number.

| Command | Behaviour |
|---|---|
| `add NAME PHONE` | If NAME exists: `NAME already exists`. Else if PHONE belongs to someone: `PHONE is already used by OTHER`. Else store it and print `Added NAME` |
| `update NAME PHONE` | If NAME is unknown: `No contact named NAME`. Else if PHONE belongs to a **different** contact: `PHONE is already used by OTHER`. Else set the new phone and print `Updated NAME` |
| `delete NAME` | `Deleted NAME`, or `No contact named NAME` |
| `phone PHONE` | `PHONE belongs to NAME`, or `Unknown number PHONE` |
| `find PREFIX` | every contact whose name starts with PREFIX, **ignoring case**, as `NAME: PHONE` lines; or `No matches` |
| `list` | every contact as `NAME: PHONE`; or `Contact book is empty` |
| `count` | `Contacts: N` |
| anything else | `Unknown command` |

`find` and `list` print contacts sorted by name **ignoring case** (`key=str.lower`); names that
are equal ignoring case keep the order in which they were added.

**Example**

Input:
```
add ravi 98111
add Asha 98200
add meena 98111
add asha 90000
find a
update ravi 98200
update ravi 97000
phone 97000
phone 98111
delete kiran
list
count
help
quit
```
Output:
```
Added ravi
Added Asha
98111 is already used by ravi
Added asha
Asha: 98200
asha: 90000
98200 is already used by Asha
Updated ravi
97000 belongs to ravi
Unknown number 98111
No contact named kiran
Asha: 98200
asha: 90000
ravi: 97000
Contacts: 3
Unknown command
Goodbye
```

`phone` lookups must be fast: the tests add 30,000 contacts and look up 30,000 numbers.
