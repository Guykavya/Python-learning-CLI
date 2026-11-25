def check_pivot(expected, pasted, tol=1e-6):
    def norm(label):
        s = str(label).strip().lower()
        return "grand total" if s == "total" else s

    exp, got = expected.copy(), pasted.copy()
    exp.index, exp.columns = [norm(x) for x in exp.index], [norm(x) for x in exp.columns]
    got.index, got.columns = [norm(x) for x in got.index], [norm(x) for x in got.columns]
    problems = [f"row only in expected: {r}" for r in sorted(set(exp.index) - set(got.index))]
    problems += [f"row only in pasted: {r}" for r in sorted(set(got.index) - set(exp.index))]
    problems += [f"column only in expected: {c}" for c in sorted(set(exp.columns) - set(got.columns))]
    problems += [f"column only in pasted: {c}" for c in sorted(set(got.columns) - set(exp.columns))]
    rows = [r for r in exp.index if r in set(got.index)]
    cols = [c for c in exp.columns if c in set(got.columns)]
    for r in rows:
        for c in cols:
            e, g = exp.loc[r, c], got.loc[r, c]
            if not abs(e - g) <= tol:
                problems.append(f"{r} / {c}: expected {e:,.2f}, pasted {g:,.2f}")
    return problems
