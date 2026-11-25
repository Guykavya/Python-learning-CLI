## Model answer

**Cached values.** openpyxl writes formulas but **no results**. A file that has only been through a script has empty cached values until Excel (or LibreOffice) opens and saves it. A reader that does not calculate (`pandas.read_excel`, `load_workbook(data_only=True)`, a phone previewer, a mail preview)
sees empty cells or `None`. When we generate the workbook we set it to **recalculate when opened** (`fullCalcOnLoad`) and we verify the numbers with an evaluator, so we know what Excel will show; with an edited file nobody knows whether the cached numbers are old.

**Round trips lose things.** `load_workbook` followed by `save` rewrites the file from openpyxl's model of it, and what the model does not cover is **dropped silently**: slicers, pivot caches, some chart options, certain images and extensions. The report looks fine in the script and is missing a feature when the manager opens it.

**Traceability and tests.** A workbook generated from pandas data has every number either written by code or computed by a formula that the code also wrote, so each figure traces to a pandas result, and a test can compare the two (the verify step) and lint the workbook (the lint step). With a hand-built file edited by a script, formulas and typed values from earlier months are mixed,
nobody knows which cells were overwritten, and the check "does the report equal the analysis?" cannot be automated.

**When to open an existing file.** To **read** numbers someone else produced (with `data_only=True` and an awareness that they may be stale), or to fill a **simple template** whose layout is stable and whose result you verify against pandas after every build.

**Checklist: your answer should mention**
- [ ] formulas have no cached value until Excel calculates; readers that do not calculate see empty cells; set fullCalcOnLoad
- [ ] a load and save round trip silently loses features openpyxl does not model
- [ ] a generated workbook can be verified against pandas and linted; an edited one cannot
- [ ] reading someone's workbook (or a simple tested template) is the exception
