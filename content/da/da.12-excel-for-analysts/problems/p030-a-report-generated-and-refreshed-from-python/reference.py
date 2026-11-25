import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.workbook.properties import CalcProperties


def build_report(orders, products, target_margin=0.40):
    n, k = len(orders), len(products)
    wb = Workbook()
    sm = wb.active
    sm.title = "Summary"
    wo, wp, wi = wb.create_sheet("Orders"), wb.create_sheet("Products"), wb.create_sheet("Inputs")
    wo.append(["order_id", "order_date", "region", "product_code", "units", "unit_price", "discount",
               "category", "unit_cost", "revenue", "cost", "margin"])
    raw = ["order_id", "order_date", "region", "product_code", "units", "unit_price", "discount"]
    for i, row in enumerate(orders[raw].itertuples(index=False), 2):
        vals = [v.to_pydatetime() if isinstance(v, pd.Timestamp) else (v.item() if hasattr(v, "item") else v) for v in row]
        wo.append(vals + [
            f"=XLOOKUP(D{i},Products!$A$2:$A${k + 1},Products!$C$2:$C${k + 1})",
            f"=XLOOKUP(D{i},Products!$A$2:$A${k + 1},Products!$D$2:$D${k + 1})",
            f"=E{i}*F{i}*(1-G{i})", f"=E{i}*I{i}", f"=J{i}-K{i}"])
    wp.append(["code", "product", "category", "unit_cost"])
    for row in products[["code", "product", "category", "unit_cost"]].itertuples(index=False):
        wp.append([v.item() if hasattr(v, "item") else v for v in row])
    wi["A1"], wi["B1"] = "Target gross margin", target_margin
    for name, col in (("Order_Date", "B"), ("Region", "C"), ("Units", "E"), ("Category", "H"), ("Rev", "J"), ("Cost", "K"), ("Margin", "L")):
        wb.defined_names[name] = DefinedName(name, attr_text=f"Orders!${col}$2:${col}${n + 1}")
    wb.defined_names["Target_Margin"] = DefinedName("Target_Margin", attr_text="Inputs!$B$1")
    sm["A1"] = "Sales report"
    for r, (label, f) in enumerate([("Revenue", "=SUM(Rev)"), ("Gross margin", "=SUM(Margin)"), ("Gross margin %", "=B4/B3"),
                                     ("Status", '=IF(B5>=Target_Margin,"on target","below target")')], 3):
        sm[f"A{r}"], sm[f"B{r}"] = label, f
    regions, cats = sorted(orders["region"].unique()), sorted(products["category"].unique())
    sm["A8"] = "Region"
    for j, c in enumerate(cats):
        sm.cell(8, 2 + j, c)
    for i, reg in enumerate(regions):
        sm.cell(9 + i, 1, reg)
        for j in range(len(cats)):
            col = get_column_letter(2 + j)
            sm.cell(9 + i, 2 + j, f"=SUMIFS(Rev,Region,$A{9 + i},Category,{col}$8)")
    sm.conditional_formatting.add("B6", CellIsRule(operator="equal", formula=['"below target"'], font=Font(color="C00000", bold=True)))
    wo.freeze_panes = wp.freeze_panes = "A2"
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    return wb
