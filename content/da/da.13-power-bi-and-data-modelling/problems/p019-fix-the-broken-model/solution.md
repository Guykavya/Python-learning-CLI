## Approach

Each fault shows up in a different test: the value test fails in every context that involves the missing dimension or the discount; the reachability test flags a measure that does not change when sliced; the lint would flag a table without relationships. Fixing them one at a time and rerunning the tests is the method.

## Code

```python
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
```

## Complexity

O(rows) per evaluation.

## Another way

Keep the measures in a list (name, DAX, description) and the relationships in a list, and build the model from them (problem 20): a fault is then visible in a diff of two small text files.
