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
