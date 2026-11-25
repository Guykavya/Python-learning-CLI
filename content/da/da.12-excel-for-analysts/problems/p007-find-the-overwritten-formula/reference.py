from openpyxl.formula.translate import Translator


def column_consistency(ws, col, first_row=2):
    base = ws[f"{col}{first_row}"].value
    if not (isinstance(base, str) and base.startswith("=")):
        raise ValueError("the first row is not a formula")
    bad = []
    for r in range(first_row + 1, ws.max_row + 1):
        v = ws[f"{col}{r}"].value
        want = Translator(base, origin=f"{col}{first_row}").translate_formula(f"{col}{r}")
        if v != want:
            bad.append((r, v))
    return bad
