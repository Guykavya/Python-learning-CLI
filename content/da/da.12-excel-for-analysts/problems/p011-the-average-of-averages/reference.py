def add_price_metrics(wb, region):
    ws = wb["Summary"] if "Summary" in wb.sheetnames else wb.create_sheet("Summary")
    ws["A1"], ws["B1"] = "Average line price", f'=AVERAGEIFS(Price,Region,"{region}")'
    ws["A2"], ws["B2"] = "Revenue per unit", f'=SUMIFS(Rev,Region,"{region}")/SUMIFS(Units,Region,"{region}")'
    return ws
