def add_margin_column(ws, n_rows, rate_cell="$M$1"):
    ws["E1"] = "margin"
    for r in range(2, n_rows + 2):
        ws[f"E{r}"] = f"=B{r}*C{r}-B{r}*D{r}*(1+{rate_cell})"
