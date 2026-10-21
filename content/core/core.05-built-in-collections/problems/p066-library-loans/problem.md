# Library loans

Run a small library. Titles and member names are single words. Read commands until `close`:

| Command | Behaviour |
|---|---|
| `addbook TITLE N` | add N copies of TITLE. Print `TITLE: K copies available` (K after adding) |
| `borrow MEMBER TITLE` | see the rules below; on success print `MEMBER borrowed TITLE` |
| `return MEMBER TITLE` | if MEMBER has TITLE: print `MEMBER returned TITLE`; otherwise `MEMBER does not have TITLE` |
| `member MEMBER` | `MEMBER has: t1, t2` (titles sorted), or `MEMBER has nothing` |

Borrowing rules, checked **in this order**:

1. unknown title: `No such book TITLE`
2. member already has this title: `MEMBER already has TITLE`
3. member already has 3 books: `MEMBER has reached the limit`
4. no copies left: `TITLE is not available`

After `close`, print every title sorted, as `TITLE: available/total`.

**Example**

Input:
```
addbook dune 1
addbook emma 2
borrow asha dune
borrow ravi dune
borrow asha dune
borrow asha emma
member asha
return ravi dune
return asha dune
borrow ravi dune
borrow asha zen
member kiran
close
```
Output:
```
dune: 1 copies available
emma: 2 copies available
asha borrowed dune
dune is not available
asha already has dune
asha borrowed emma
asha has: dune, emma
ravi does not have dune
asha returned dune
ravi borrowed dune
No such book zen
kiran has nothing
dune: 0/1
emma: 1/2
```
