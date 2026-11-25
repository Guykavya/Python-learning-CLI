def build_model(Model, tables):
    """Model is the chapter's engine class (passed in); tables is a dict of DataFrames: Date, Product, Customer, Store, Sales, Orders."""
    m = Model()
    for name in ("Date", "Product", "Customer", "Store", "Sales", "Orders"):
        m.table(name, tables[name])
    m.relate("Sales", "OrderDateKey", "Date", "DateKey")
    m.relate("Sales", "ShipDateKey", "Date", "DateKey", active=False)
    m.relate("Sales", "ProductKey", "Product", "ProductKey")
    m.relate("Sales", "CustomerKey", "Customer", "CustomerKey")
    m.relate("Sales", "StoreKey", "Store", "StoreKey")
    m.relate("Orders", "OrderDateKey", "Date", "DateKey")
    m.relate("Orders", "CustomerKey", "Customer", "CustomerKey")
    m.relate("Orders", "StoreKey", "Store", "StoreKey")
    m.measure("Revenue", "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))")
    m.measure("Quantity", "SUM(Sales[Quantity])")
    m.measure("Orders", "DISTINCTCOUNT(Sales[OrderID])")
    m.measure("Customers", "DISTINCTCOUNT(Sales[CustomerKey])")
    m.measure("Cost", "SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))")
    m.measure("Margin", "[Revenue] - [Cost]")
    m.measure("Margin %", "DIVIDE([Margin], [Revenue])")
    m.measure("Freight", "SUM(Orders[Freight])")
    return m
