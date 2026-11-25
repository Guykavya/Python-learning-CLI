MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "Cost": "SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))",
    "Margin": "[Revenue] - [Cost]",
    "Margin %": "DIVIDE([Margin], [Revenue])",
}
