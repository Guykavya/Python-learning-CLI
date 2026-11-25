MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "Orders": "DISTINCTCOUNT(Sales[OrderID])",
    "Average order value": "DIVIDE([Revenue], [Orders])",
}
