## Hint 1

For each line of the script, ask: "what is this line really waiting for, and how does it know it has happened?" A sleep knows nothing; it only lets time pass. Then look up, in the table of section 11.4, which Playwright feature checks the thing itself: an element, a response, a download.

## Hint 2

Match each bug to a cause: `0 rows` on slow days (a time guess plus a method that does not wait), a broken click after a redesign (a selector tied to layout), last week's file (reading a file by name instead of the file this click produced). Each has a one-line fix in section 11.4: `expect(...).to_be_visible()`, `get_by_role(...)`, `page.expect_download()`.
