# Wait for the right thing

Chapter sections 11.4 (the five ideas that make browser scripts robust), 11.5 (browser automation traps) and "Try it: wait for the right thing". Playwright is not installed in the course environment, so this is a reading and reasoning problem: no browser is needed.

A teammate's weekly job downloads a report from an internal dashboard:

```python
page.goto("https://reports.example.com/dashboard")
time.sleep(3)                                                       # "the table needs time"
rows = page.locator("tr").count()
print(f"{rows} rows")
page.locator("div.main > div:nth-child(3) > div > button.btn-primary").click()   # "Export CSV"
time.sleep(5)                                                       # "the download takes a while"
shutil.copy(os.path.expanduser("~/Downloads/report.csv"), "weekly.csv")
```

On most weeks it works. Some Mondays it prints `0 rows`; after the dashboard's redesign it fails on the click; once it copied **last week's** `report.csv`.

In `answer.md` (about 250 to 400 words):

1. Explain why `time.sleep(3)` is **flaky**: what happens when the page is slower than 3 seconds, and what it costs when it is faster.
2. Say what to wait for instead for the table: an **element state** (with code), and explain why `locator("tr").count()` does not wait while locator **actions** do.
3. Replace the CSS path with a **stable locator** and explain why role, label or text beat `div > div:nth-child(3)`.
4. Replace the second sleep: wait for the **download event** (`page.expect_download()`), and explain how this also fixes the "last week's file" bug.
5. Name two more safety measures from section 11.4 or 11.5 this job needs (timeouts, evidence on failure, credentials, ...).

## Example

A good sentence for part 1: "A fixed sleep guesses how long the page needs. When the server is slow on Monday mornings the guess is too short and the script counts an empty table; on fast days it wastes the rest of the 3 seconds on every run. Waiting for a condition takes exactly as long as needed, up to a timeout."
