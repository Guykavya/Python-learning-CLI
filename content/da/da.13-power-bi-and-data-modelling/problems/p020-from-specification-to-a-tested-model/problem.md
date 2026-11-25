# From specification to a tested model

Chapter section 9 (the project). A model that only lives in a Power BI file cannot be reviewed or tested. Describe it as **data**: the tables (files), the relationships and the measures in a JSON **specification**, and rebuild the model from it. Then check that a **report specification** only uses fields and measures that exist. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

**1. `model_from_project(folder, Model)`**: `folder` (a `pathlib.Path`) holds `model_spec.json` and the data files. The spec is

```text
{"tables": {"Date": {"file": "DimDate.parquet"}, "Sales": {"file": "FactSales.csv"}, ...},
 "relationships": [{"from": "Sales[OrderDateKey]", "to": "Date[DateKey]", "direction": "single", "active": true}, ...],
 "measures": [{"name": "Revenue", "dax": "SUMX(...)"}, ...]}
```

Build `m = Model()`; add each table (read `.parquet` with `pd.read_parquet`, `.csv` with `pd.read_csv`; the files are in the same folder), then each relationship (`from` is the **many** side, `to` the **one** side, both written `Table[Column]`; `direction == "both"` makes it bidirectional), then each measure in order. Return `(m, spec)` (the spec as a dict).
If the engine refuses a relationship (the one side is not unique), raise `ValueError("relationship <from> -> <to>: <the engine's message>")`.

**2. `check_report_spec(report, model, spec)`** returns a list of problems (empty when the report is fine). `report` is a dict `{page: {"slicers": [...], "visuals": [...]}}`; a visual may have `measure` or `measures` (a name or a list), and `axis`, `rows`, `columns` (each a field `Table[Column]`). Messages, in the order found (pages in dict order, slicers first, then each visual: measures, then `axis`, `rows`, `columns`):

- `"<page>: slicer field <Table[Column]> does not exist"`;
- `"<page>: measure [<name>] does not exist"` (measure names come from `spec["measures"]`);
- `"<page>: field <Table[Column]> does not exist"` for the axis, rows and columns.

A field exists when the table is in `model.t` and the column is in that table. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

## Example

A visual with `{"type": "card", "measure": "Revnue"}` on the page `Overview` gives `Overview: measure [Revnue] does not exist`.
