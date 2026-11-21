## Model answer

**1. Why `sleep(3)` is flaky.** A sleep is a guess about time, not a check of the page. When the dashboard is slower than 3 seconds (Monday morning, a big report, a slow VPN), the script continues before the table exists and counts 0 rows, a wrong answer that looks valid. When the page is faster, every run wastes the remaining time. Raising the number only moves the problem: too short is flaky, too long is slow, and there is no right value.

**2. Wait for an element state.** Wait for the thing you need: `page.wait_for_selector("tr.data-row")` or, better, `expect(page.locator("tr.data-row").first).to_be_visible()`, then `count()`. Playwright's **actions** (`click`, `fill`, `inner_text`) auto-wait until the element is attached, visible and enabled; `count()` is a question about **now**, so it returns 0 immediately if the rows are not there yet. `expect(...)` assertions retry until true or until the timeout. Waiting for the network response that fills the table (`page.expect_response("**/api/report*")`) is another good condition.

**3. Stable locators.** `page.get_by_role("button", name="Export CSV")` describes what the user sees. The CSS path describes the page's **layout** (third child of a div), and a redesign that moves the button, adds a banner or changes a class breaks it, even though the button still says "Export CSV". Meanings change slowly; layouts change often. If text is ambiguous, ask the developers for a `data-testid`.

**4. Wait for the download.** `with page.expect_download() as info: page.get_by_role("link", name="Export CSV").click()` then `info.value.save_as("weekly.csv")`. The script waits for **this** download event, however long it takes (up to the timeout), and saves exactly the file the click produced. Copying `~/Downloads/report.csv` after a sleep picks up whatever file has that name, which after a failed or slow download was last week's: a silent wrong result.

**5. More safety.** Set `page.set_default_timeout(15_000)` so a hung page fails in 15 seconds instead of blocking the scheduled job; record a trace on failure (`context.tracing.start(screenshots=True, snapshots=True)`, saved when an exception happens) so you can see what the page looked like; take credentials from the environment and reuse a saved login state (`storage_state`) protected like a password; check the row count is above zero and exit non-zero otherwise (fail loudly); and first look for an API or export URL, because a browser is the slowest and most fragile option (section 10).

**Checklist: your answer should mention**
- [ ] a sleep is a guess: too short gives wrong results, too long wastes time
- [ ] wait for a condition: element visible (`wait_for_selector` / `expect(...).to_be_visible()`) or a network response
- [ ] `count()` does not wait; actions and `expect` do
- [ ] role, label, text or `data-testid` locators survive redesigns; CSS layout paths do not
- [ ] `expect_download()` ties the file to the click and fixes the stale-file bug
- [ ] at least two of: timeouts, trace on failure, credentials from the environment, failing loudly on 0 rows, prefer an API
