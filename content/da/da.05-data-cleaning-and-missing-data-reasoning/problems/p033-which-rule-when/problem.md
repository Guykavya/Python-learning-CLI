# Which rule when?

Chapter section 9.7 and 8.5. There is no formula for handling missing values, but there are sensible defaults that
start from the **reason** a value is missing. For each of the four cases in `answer.md` below, say what the missing
value means, what you do (drop, fill with what, leave missing, interpolate), and what you write in the report. Use
about 250 to 350 words in total.

1. **A temperature sensor** misses one reading at 14:00 on a day with readings every hour.
2. **A survey** where 30 percent of the people did not answer the income question, and the people who skipped are
   mostly young.
3. **A product** that has no rows in the sales table for a week in which the shop was open.
4. **A test score** that is empty for a student who was absent on the exam day.

Finish with one sentence: if your choice could change the headline number, what do you show next to it?

## Example

A start: "First I ask what the missing value *means*. For the sensor, a one-hour gap is a short outage in a smooth
process, so I would interpolate between the neighbours, but only for short gaps..."
