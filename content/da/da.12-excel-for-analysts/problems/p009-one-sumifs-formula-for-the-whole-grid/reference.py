from openpyxl.utils import get_column_letter


def add_grid(wb, regions, cats, top, left=1):
    ws = wb["Summary"] if "Summary" in wb.sheetnames else wb.create_sheet("Summary")
    ws.cell(top, left, "Region")
    for j, c in enumerate(cats):
        ws.cell(top, left + 1 + j, c)
    lab = get_column_letter(left)
    for i, region in enumerate(regions):
        row = top + 1 + i
        ws.cell(row, left, region)
        for j in range(len(cats)):
            col = get_column_letter(left + 1 + j)
            ws.cell(row, left + 1 + j, f"=SUMIFS(Rev,Region,${lab}{row},Category,{col}${top})")
    return ws
