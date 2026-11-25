import numpy as np
import pandas as pd
import pytest

import io

from openpyxl import Workbook, load_workbook

from solution import add_checks


def make(**kw):
    ws = Workbook().active
    ws.append(["id", "region", "revenue", "margin"])
    for i in range(1, 6):
        ws.append([i, "North", 100.0, 0.30 + 0.05 * i])
    add_checks(ws, 5, 0.40, ["North", "South", "East"], **kw)
    return ws


def rules(ws):
    out = []
    for cf in ws.conditional_formatting:
        for r in cf.rules:
            out.append((str(cf.sqref), r))
    return out


def test_conditional_format_on_the_margin_column():
    found = rules(make())
    assert len(found) == 1, f"one conditional-format rule expected, found {len(found)}."
    rng, r = found[0]
    assert rng == "D2:D6", f"the rule covers the data rows of column D (D2:D6), got {rng}"
    assert r.type == "cellIs" and r.operator == "lessThan" and r.formula == ["0.4"], f"a cellIs rule 'lessThan 0.4'; got {r.type}, {r.operator}, {r.formula}"
    assert r.dxf.font.b and r.dxf.font.color.rgb.endswith("C00000"), "red bold font."
    assert r.dxf.fill.bgColor.rgb.endswith("F4B183") or r.dxf.fill.start_color.rgb.endswith("F4B183"), "light red fill."


def test_dropdown_validation():
    ws = make()
    dvs = ws.data_validations.dataValidation
    assert len(dvs) == 1, "one data validation expected (did you call ws.add_data_validation?)."
    dv = dvs[0]
    assert dv.type == "list" and dv.formula1 == '"North,South,East"', f"list text must be quoted: \"North,South,East\"; got {dv.formula1!r}"
    assert str(dv.sqref) == "H1" and dv.allow_blank is False and dv.showErrorMessage is True, "on H1, no blanks, with an error message."
    assert dv.error, "give the error message a text."


def test_other_input_cell_and_save_round_trip():
    ws = make(input_cell="K3")
    assert str(ws.data_validations.dataValidation[0].sqref) == "K3"
    buf = io.BytesIO()
    ws.parent.save(buf)
    buf.seek(0)
    back = load_workbook(buf).active
    assert len(back.data_validations.dataValidation) == 1 and len(rules(back)) == 1, "both features survive saving and reloading."
