# Syncing LeetCode and Codeforces with the learning module

This guide explains how your LeetCode and Codeforces work gets recorded in
the module, what can be synced automatically, and what you log by hand.

> **Status:** the engine is built and these commands work. Your accounts
> (`neuralkiwi` on Codeforces, `kavya1416` on LeetCode) are already saved in
> `config.toml`. Run commands as `./learn ...` from this folder, or just `learn ...`
> inside a VS Code terminal that has the `.venv` environment active.

---

## 1. The big picture

The module keeps one tracker database on your laptop. Problems reach it from
three places:

| Source | How it gets in | Automatic? |
|---|---|---|
| Local module problems | `learn check` runs the tests and records the result | Yes |
| Codeforces | `learn sync cf` calls the official Codeforces API | Yes, fully |
| LeetCode | `learn sync lc` reads your public profile, `learn log lc` adds code and notes | Partly |

Your **solution code always lives in this folder** (`my-work/dsa/...`), not
only on the websites. If a site disappears or changes, your history stays.

---

## 2. Codeforces

### 2.1 One-time setup

1. Create an account at https://codeforces.com/register.
2. Your **handle** is your username. You see it at the top right after login
   and in your profile URL: `https://codeforces.com/profile/<handle>`.
3. Give the handle to the module once:

   ```
   learn config set accounts.codeforces_handle <your_handle>
   ```

No password, no API key, no login is needed. Codeforces publishes submissions
of every user publicly through its official API.

### 2.2 What the API gives

The engine uses three official endpoints:

| Endpoint | What it returns |
|---|---|
| `user.info?handles=<handle>` | rating, max rating, rank |
| `user.status?handle=<handle>` | every submission: problem, verdict, language, time, problem tags and difficulty rating |
| `user.rating?handle=<handle>` | rating change after each contest |

From this the engine records every **accepted** problem, counts wrong attempts
before acceptance, and maps Codeforces tags (for example `dp`, `graphs`,
`binary search`) onto the DSA modules in `syllabus.yaml`.

**Rule:** Codeforces allows about **one request every 2 seconds**. The engine
waits between calls. If you write your own scripts, do the same.

### 2.3 Test it yourself (works today)

Save this as `scratch/cf_test.py` and run `python3 scratch/cf_test.py <handle>`:

```python
import json
import sys
import urllib.request

handle = sys.argv[1]
url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=20"

with urllib.request.urlopen(url, timeout=15) as resp:
    data = json.load(resp)

if data["status"] != "OK":
    print("Error:", data.get("comment"))
    sys.exit(1)

for sub in data["result"]:
    p = sub["problem"]
    name = f'{p.get("contestId")}{p["index"]} {p["name"]}'
    print(f'{sub.get("verdict", "?"):22} {name:45} rating={p.get("rating", "-")} tags={p["tags"]}')
```

You should see your last 20 submissions with verdicts like `OK` (accepted),
`WRONG_ANSWER` or `TIME_LIMIT_EXCEEDED`.

### 2.4 Daily flow

1. Solve a problem on Codeforces (in a contest or the problemset).
2. Copy your final code into `my-work/dsa/<pattern>/cf-<contest><index>.py`.
   The engine creates this file for you with `learn log cf <contest><index>`.
3. Run `learn sync cf`. Accepted problems, attempts and tags appear in your stats.

---

## 3. LeetCode

### 3.1 One-time setup

1. Create an account at https://leetcode.com.
2. Your **username** is in your profile URL: `https://leetcode.com/u/<username>/`.
3. Keep your profile **public** (it is public by default).
4. Give the username to the module once:

   ```
   learn config set accounts.leetcode_username <your_username>
   ```

### 3.2 What can and cannot be synced

LeetCode has **no official public API**. The website itself uses a GraphQL
endpoint (`https://leetcode.com/graphql`), and some data from it is readable
for any public profile without logging in:

| Data | Available without login? |
|---|---|
| Total solved count (easy, medium, hard) | Yes |
| Your **most recent accepted** problems, roughly the last 20 | Yes |
| Your full submission history | No |
| Your submitted code | No |

That is why LeetCode is **partly** automatic:

- `learn sync lc` pulls your solve counts and recent accepted problems.
  **Run it at least every few days**, otherwise older solves fall off the
  "recent" list before the engine sees them.
- `learn log lc <problem-slug>` saves your code, the pattern, time taken and
  your key insight. This is the part that actually builds your skill, so do
  it after every LeetCode solve.

The problem slug is the part of the URL after `/problems/`. For
`https://leetcode.com/problems/two-sum/` the slug is `two-sum`.

> **Security rule:** never paste your LeetCode session cookie or password into
> any script, including this module. Everything here works with public data only.

> **Fragility:** because the endpoint is unofficial, LeetCode can change it
> without notice. If sync breaks, `learn log lc` keeps working because it
> needs no network at all.

### 3.3 Test it yourself (works today)

Save this as `scratch/lc_test.py` and run `python3 scratch/lc_test.py <username>`:

```python
import json
import sys
import urllib.request

username = sys.argv[1]
query = """
query($u: String!, $l: Int!) {
  matchedUser(username: $u) {
    submitStatsGlobal { acSubmissionNum { difficulty count } }
  }
  recentAcSubmissionList(username: $u, limit: $l) {
    title titleSlug timestamp
  }
}
"""
body = json.dumps({"query": query, "variables": {"u": username, "l": 20}}).encode()
req = urllib.request.Request(
    "https://leetcode.com/graphql",
    data=body,
    headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.load(resp)["data"]

if data["matchedUser"] is None:
    print("User not found or profile is private.")
    sys.exit(1)

for row in data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]:
    print(f'{row["difficulty"]:7} solved: {row["count"]}')

print("\nRecent accepted:")
for s in data["recentAcSubmissionList"]:
    print(f'  {s["titleSlug"]}')
```

### 3.4 Daily flow

1. Solve the problem on LeetCode.
2. Run `learn log lc <slug>`. It asks for:
   - your final code (or opens the file for you to paste into),
   - the pattern, for example `sliding-window`,
   - minutes taken and hints used,
   - one or two lines on the key insight.
3. Every few days run `learn sync lc` to confirm and catch anything you forgot to log.

---

## 4. CSES (bonus)

The CSES Problem Set (https://cses.fi/problemset/) is a free, well-ordered set
of about 400 classic problems. It has no public API, so it works like
LeetCode logging: `learn log cses <task-id>`.

---

## 5. How it all shows up

```
$ learn stats dsa
  Pattern            Local   LC   CF   CSES   Mastery
  two-pointers         12     8    3     2    ███████░░░
  sliding-window        9     6    1     0    █████░░░░░
  binary-search         4     2    0     1    ██░░░░░░░░
  dynamic-programming   0     0    0     0    not started
```

The engine also lists patterns from the syllabus you have **never practised**,
so gaps are always visible.

---

## 6. Troubleshooting

| Problem | Cause and fix |
|---|---|
| Codeforces says `handle: User with handle ... not found` | Check spelling and case in your profile URL |
| Codeforces returns `Call limit exceeded` | Too many requests; wait a few seconds |
| LeetCode `matchedUser` is `null` | Wrong username or private profile |
| LeetCode recent list is empty | No accepted submissions recently, or the list is hidden; use `learn log lc` |
| Network errors | Both sites need internet; everything else in the module works offline |
