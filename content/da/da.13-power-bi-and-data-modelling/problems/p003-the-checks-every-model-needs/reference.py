def check_star(facts, dims, keys):
    issues = []
    for dname, d in dims.items():
        key = d.columns[0]
        if not d[key].is_unique:
            issues.append(f"{dname}[{key}] has duplicate keys")
        if d[key].isna().any():
            issues.append(f"{dname}[{key}] has blank keys")
    for fname, fcol, dname, dcol in keys:
        col = facts[fname][fcol]
        nulls = int(col.isna().sum())
        orphans = int((~col.dropna().isin(dims[dname][dcol])).sum())
        if nulls:
            issues.append(f"{fname}[{fcol}] has {nulls} blank keys")
        if orphans:
            issues.append(f"{fname}[{fcol}] has {orphans} orphan rows (not in {dname}[{dcol}])")
    return issues
