# Which file format when?

Chapter section 6. Choose a format for each of the five situations below, and give the reason in one or two sentences.
Write your answer in `answer.md`, in about 150 to 250 words.

1. You must hand a table of last month's sales to a manager who works in Excel and wants to filter it by hand.
2. Your cleaning script produces a table that the **next script** will load. It has dates, integer ids with gaps and text codes with leading zeros.
3. A table with 50 million rows, of which each analysis reads only 3 columns.
4. A web service sends you orders with customers and a list of items inside each order.
5. The company already keeps the orders in a database, and you only need last week's rows for one customer.

## Example

A start: "1. Excel (`.xlsx`): the manager opens it directly, and `to_excel(index=False)` gives clean sheets..."
