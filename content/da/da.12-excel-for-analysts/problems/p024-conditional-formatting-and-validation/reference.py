from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation


def add_checks(ws, n_rows, target, regions, input_cell="H1"):
    rule = CellIsRule(operator="lessThan", formula=[str(target)],
                      font=Font(color="C00000", bold=True), fill=PatternFill("solid", start_color="F4B183"))
    ws.conditional_formatting.add(f"D2:D{n_rows + 1}", rule)
    dv = DataValidation(type="list", formula1='"' + ",".join(regions) + '"', allow_blank=False,
                        showErrorMessage=True, errorTitle="Region", error="Pick a region from the list")
    ws.add_data_validation(dv)
    dv.add(input_cell)
