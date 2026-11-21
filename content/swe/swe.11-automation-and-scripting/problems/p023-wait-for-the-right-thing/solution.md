## Approach

The model answer is in `answer.md`. The common idea behind all three bugs: the script **assumed** something instead of **checking** it. It assumed the table appears within 3 seconds, assumed the layout stays the same, assumed the newest `report.csv` is this week's. Robust automation replaces every assumption with a condition the tool can wait for, plus a timeout so "never" becomes a clear failure.

## Cost

Reading only. In a real job the fixes make the script both faster (no wasted sleep) and more reliable.

## Another way

Ask whether you need a browser at all (section 10): the "Export CSV" button probably calls a URL such as `/api/report.csv?week=47`. If you are allowed to use it, an HTTP request with a timeout and a check of the status code replaces the whole script, with no waiting problems at all.
