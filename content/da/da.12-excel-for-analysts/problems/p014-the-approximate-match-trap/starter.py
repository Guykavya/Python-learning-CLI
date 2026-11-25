def add_prices(wb):
    # Approximate match on UNSORTED codes: some prices are silently wrong. Fix it (exact match, 'not found' for missing codes).
    orders, k = wb["Orders"], wb["Products"].max_row
    orders["C1"] = "price"
    for r in range(2, orders.max_row + 1):
        orders[f"C{r}"] = f"=VLOOKUP(B{r},Products!$A$2:$B${k},2)"
