MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "% of category": "DIVIDE([Revenue], CALCULATE([Revenue], ALLEXCEPT(Product, Product[Category])))",
}
