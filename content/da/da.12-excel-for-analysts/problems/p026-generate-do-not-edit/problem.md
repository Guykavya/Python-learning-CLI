# Generate, do not edit

Chapters 10.5 and 10.6. A colleague proposes: "We already have a nice Excel report with charts and formatting made by hand. Let's write a small script that **opens that file with openpyxl, pastes the new numbers in and saves it**, every month."

In `answer.md`, in about 250 to 350 words, explain why the course builds the report **from scratch in Python each time** instead. Cover at least:

1. what happens to the **cached values** (what a reader of the file sees before Excel recalculates it);
2. what a **load and save round trip** can lose;
3. why generating the workbook from code makes the **numbers traceable** to pandas and testable;
4. the one situation in which opening an existing file is the right tool.

## Example

A start: "When openpyxl saves a workbook it writes the formulas but no results. A reader that does not calculate, such as pandas or a previewer on a phone, sees empty cells..."
