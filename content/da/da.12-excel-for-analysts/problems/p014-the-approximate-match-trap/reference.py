def add_prices(wb):
    orders, k = wb["Orders"], wb["Products"].max_row
    orders["C1"] = "price"
    for r in range(2, orders.max_row + 1):
        orders[f"C{r}"] = f'=IFERROR(VLOOKUP(B{r},Products!$A$2:$B${k},2,FALSE),"not found")'
