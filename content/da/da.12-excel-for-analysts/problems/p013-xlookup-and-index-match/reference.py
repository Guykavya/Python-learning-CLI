def add_price_lookup(wb, how):
    if how not in ("xlookup", "index_match"):
        raise ValueError("how must be 'xlookup' or 'index_match'")
    orders, k = wb["Orders"], wb["Products"].max_row
    orders["C1"] = "price"
    for r in range(2, orders.max_row + 1):
        if how == "xlookup":
            orders[f"C{r}"] = f'=XLOOKUP(B{r},Products!$A$2:$A${k},Products!$B$2:$B${k},"not found")'
        else:
            orders[f"C{r}"] = f'=IFNA(INDEX(Products!$B$2:$B${k},MATCH(B{r},Products!$A$2:$A${k},0)),"not found")'
