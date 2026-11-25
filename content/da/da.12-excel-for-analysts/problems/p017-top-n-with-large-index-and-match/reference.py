def add_top3(wb):
    wp = wb["Products"]
    n = wp.max_row
    if n - 1 < 3:
        raise ValueError("need at least 3 products")
    wp["C1"] = "rank_key"
    for r in range(2, n + 1):
        wp[f"C{r}"] = f"=B{r}-(COUNTIF($B$2:B{r},B{r})-1)/1000000"
    ws = wb.create_sheet("Top3")
    ws.append(["rank", "code", "revenue"])
    pos = f"MATCH(LARGE(Products!$C$2:$C${n},A{{r}}),Products!$C$2:$C${n},0)"
    for k in (1, 2, 3):
        r = k + 1
        p = pos.format(r=r)
        ws.append([k, f"=INDEX(Products!$A$2:$A${n},{p})", f"=INDEX(Products!$B$2:$B${n},{p})"])
