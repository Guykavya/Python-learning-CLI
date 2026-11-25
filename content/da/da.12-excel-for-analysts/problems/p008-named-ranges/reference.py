from openpyxl.workbook.defined_name import DefinedName


def set_names(wb, n_rows, sheet="Orders"):
    for name, col in (("Region", "B"), ("Cat", "C"), ("Rev", "D")):
        wb.defined_names[name] = DefinedName(name, attr_text=f"{sheet}!${col}$2:${col}${n_rows + 1}")
