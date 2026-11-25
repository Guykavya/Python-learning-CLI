## Hint 1

Think about three readers of the file: Excel (recalculates), pandas / a previewer (reads what is stored), and a person comparing with the numbers from the analysis. What does each see?

## Hint 2

Section 10.6 lists what `load_workbook` does not keep (slicers, some chart features, pivot caches, images in some cases). Section 12 shows the build/verify/refresh loop that a generated report allows.
