## Approach

Accounts that share an address are one person, and "share" is transitive through chains. So people are the **connected components** of a graph whose vertices are accounts and whose edges are shared addresses (chapter section 9). Union-Find builds the components while reading: the dictionary `owner` remembers the first account that used each address, and any later account with the same address is united with it. Uniting with that first owner is enough, because Union-Find merges whole groups: a chain `A - B - C` ends in one group even if `A` and `C` share nothing directly.

At the end every address belongs to the root of its owner's group. All accounts of a group carry the same name, so the root account's name is the person's name. Sorting the addresses and then the accounts gives the required output.

```python
def merge_accounts(accounts):
    parent = list(range(len(accounts)))

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    owner = {}                                     # address -> first account that had it
    for i, account in enumerate(accounts):
        for email in account[1:]:
            if email in owner:
                ri, rj = find(i), find(owner[email])
                if ri != rj:
                    parent[ri] = rj
            else:
                owner[email] = i
    groups = {}
    for email, i in owner.items():
        groups.setdefault(find(i), set()).add(email)
    result = [[accounts[root][0]] + sorted(emails) for root, emails in groups.items()]
    result.sort(key=lambda acc: (acc[0], acc[1]))
    return result
```

## Complexity

With `A` addresses in total: the Union-Find part is nearly `O(A)`, and sorting the addresses is `O(A log A)`.

## Another way

Build the graph on **addresses**: connect the first address of each account to its other addresses, then run BFS or DFS from every unvisited address; each search collects one person's addresses (and you keep a map address -> name). It is the same components, built explicitly. The brute force (repeatedly merge any two groups that overlap until nothing changes) is `O(n^2)` per round.
