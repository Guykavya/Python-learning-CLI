MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "Kitchen revenue": 'CALCULATE([Revenue], Product[Category] = "Kitchen")',
    "% of all revenue": "DIVIDE([Revenue], CALCULATE([Revenue], ALL(Product)))",
}
