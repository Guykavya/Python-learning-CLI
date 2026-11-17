# Accounts merge

A website exported its user accounts. Each account is a list: the first item is a **name**, the rest are **e-mail addresses** (at least one). The same person may have opened several accounts. Two accounts belong to the same person if they share **at least one** e-mail address, directly or through a chain of accounts (`A` shares an address with `B`, `B` shares one with `C`: all three are one person). Accounts that share an address always have the same name. Two accounts with the same name but no shared address (directly or through a chain) are **different** people.

Write `merge_accounts(accounts)`. Return one account per person: `[name, e-mail, e-mail, ...]` with the person's addresses **sorted** and without duplicates. Sort the returned accounts by name, and accounts with the same name by their first (smallest) address.

This is chapter section 9's `merge_accounts`, with names added. Union-Find over the **accounts**: remember for every address the first account that had it; when an address shows up again, unite the two accounts.

## Example

```python
>>> merge_accounts([
...     ["John", "johnsmith@mail.com", "john_newyork@mail.com"],
...     ["John", "johnsmith@mail.com", "john00@mail.com"],
...     ["Mary", "mary@mail.com"],
...     ["John", "johnnybravo@mail.com"],
... ])
[['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com'],
 ['John', 'johnnybravo@mail.com'],
 ['Mary', 'mary@mail.com']]
```

The first two "John" accounts share `johnsmith@mail.com`: one person. The third "John" shares nothing: a different person with the same name.

## Constraints

- Up to `1000` accounts with up to `10` addresses each. Addresses are compared exactly as strings.

## Think about

Why is "merge accounts with the same name" wrong? And why is it not enough to merge each account only with the **first** earlier account that shares an address with it, without merging whole groups?
