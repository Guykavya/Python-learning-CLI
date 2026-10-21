"""Pull solved problems from Codeforces (official API) and LeetCode (public profile data).

Only public data is used. No passwords, cookies or API keys.
"""

from __future__ import annotations

import json
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime

from learn import db

USER_AGENT = "learn-engine/0.1 (personal study tracker)"

# Codeforces tags -> DSA modules
CF_TAG_MODULES = {
    "implementation": ["dsa.00"], "brute force": ["dsa.00"], "constructive algorithms": ["dsa.00"],
    "math": ["dsa.02"], "number theory": ["dsa.02"], "combinatorics": ["dsa.02"],
    "bitmasks": ["dsa.02"], "probabilities": ["dsa.02"],
    "two pointers": ["dsa.03"],
    "hashing": ["dsa.04"],
    "sortings": ["dsa.05"],
    "binary search": ["dsa.06"], "ternary search": ["dsa.06"],
    "divide and conquer": ["dsa.07"],
    "trees": ["dsa.10"],
    "graphs": ["dsa.12"], "dfs and similar": ["dsa.12"], "shortest paths": ["dsa.12"],
    "dsu": ["dsa.12"], "graph matchings": ["dsa.12"], "flows": ["dsa.12"],
    "greedy": ["dsa.13"],
    "dp": ["dsa.14"],
    "strings": ["dsa.15"], "string suffix structures": ["dsa.15"],
    "data structures": ["dsa.16"],
    "interactive": ["dsa.17"],
}

# LeetCode topic slugs -> DSA modules
LC_TAG_MODULES = {
    "simulation": ["dsa.00"], "brainteaser": ["dsa.00"],
    "math": ["dsa.02"], "number-theory": ["dsa.02"], "combinatorics": ["dsa.02"],
    "bit-manipulation": ["dsa.02"], "geometry": ["dsa.02"],
    "array": ["dsa.03"], "string": ["dsa.03"], "prefix-sum": ["dsa.03"],
    "two-pointers": ["dsa.03"], "sliding-window": ["dsa.03"], "matrix": ["dsa.03"],
    "hash-table": ["dsa.04"], "counting": ["dsa.04"], "rolling-hash": ["dsa.04"], "hash-function": ["dsa.04"],
    "sorting": ["dsa.05"], "merge-sort": ["dsa.05"], "bucket-sort": ["dsa.05"],
    "counting-sort": ["dsa.05"], "radix-sort": ["dsa.05"], "quickselect": ["dsa.05"],
    "binary-search": ["dsa.06"],
    "backtracking": ["dsa.07"], "recursion": ["dsa.07"], "divide-and-conquer": ["dsa.07"],
    "stack": ["dsa.08"], "queue": ["dsa.08"], "monotonic-stack": ["dsa.08"], "monotonic-queue": ["dsa.08"],
    "linked-list": ["dsa.09"], "doubly-linked-list": ["dsa.09"],
    "tree": ["dsa.10"], "binary-tree": ["dsa.10"], "binary-search-tree": ["dsa.10"],
    "heap-priority-queue": ["dsa.11"],
    "graph": ["dsa.12"], "breadth-first-search": ["dsa.12"], "depth-first-search": ["dsa.12"],
    "union-find": ["dsa.12"], "topological-sort": ["dsa.12"], "shortest-path": ["dsa.12"],
    "minimum-spanning-tree": ["dsa.12"], "strongly-connected-component": ["dsa.12"],
    "greedy": ["dsa.13"],
    "dynamic-programming": ["dsa.14"], "memoization": ["dsa.14"], "bitmask": ["dsa.14"],
    "trie": ["dsa.15"], "string-matching": ["dsa.15"],
    "segment-tree": ["dsa.16"], "binary-indexed-tree": ["dsa.16"],
}


class SyncError(Exception):
    pass


def modules_for_tags(tags: list[str], mapping: dict[str, list[str]]) -> list[str]:
    out: list[str] = []
    tree_like = {"tree", "binary-tree", "binary-search-tree"}
    for tag in tags:
        mods = mapping.get(tag, [])
        # On LeetCode, DFS/BFS on a tree problem belongs to the tree module, not graphs.
        if tag in ("depth-first-search", "breadth-first-search") and tree_like & set(tags):
            mods = ["dsa.10"]
        for m in mods:
            if m not in out:
                out.append(m)
    return out


def _get_json(url: str, data: bytes | None = None, headers: dict | None = None) -> dict:
    h = {"User-Agent": USER_AGENT}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        try:
            body = json.load(exc)
        except Exception:
            body = {}
        raise SyncError(body.get("comment") or f"HTTP {exc.code} from {url.split('?')[0]}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SyncError(f"Network problem: {exc}. Everything else works offline.") from exc


def _upsert(conn: sqlite3.Connection, row: dict) -> bool:
    """Insert a synced solve. Keeps your own logged notes if the row exists. Returns True if new."""
    exists = conn.execute(
        "SELECT 1 FROM external_solves WHERE site = ? AND problem_key = ?", (row["site"], row["problem_key"])
    ).fetchone()
    if exists:
        conn.execute(
            "UPDATE external_solves SET title = COALESCE(title, ?), url = COALESCE(url, ?), "
            "tags = ?, difficulty = COALESCE(?, difficulty), "
            "modules = CASE WHEN modules IS NULL OR modules = '' THEN ? ELSE modules END, "
            "attempts = COALESCE(attempts, ?) WHERE site = ? AND problem_key = ?",
            (row["title"], row["url"], row["tags"], row["difficulty"], row["modules"], row["attempts"],
             row["site"], row["problem_key"]),
        )
        return False
    conn.execute(
        "INSERT INTO external_solves(site, problem_key, title, url, tags, difficulty, modules, solved_at, "
        "attempts, source) VALUES (:site, :problem_key, :title, :url, :tags, :difficulty, :modules, "
        ":solved_at, :attempts, 'sync')",
        row,
    )
    return True


# ---------------------------------------------------------------- Codeforces

def sync_codeforces(conn: sqlite3.Connection, handle: str) -> tuple[int, int, str]:
    if not handle:
        raise SyncError("Set your handle first: learn config set accounts.codeforces_handle <handle>")
    info = _get_json(f"https://codeforces.com/api/user.info?handles={handle}")
    time.sleep(2.1)  # Codeforces allows about one call every two seconds
    status = _get_json(f"https://codeforces.com/api/user.status?handle={handle}")
    if status.get("status") != "OK":
        raise SyncError(status.get("comment", "Codeforces returned an error"))

    attempts: dict[str, int] = {}
    accepted: dict[str, dict] = {}
    for sub in sorted(status["result"], key=lambda s: s["creationTimeSeconds"]):
        p = sub["problem"]
        key = f'{p.get("contestId", "")}{p["index"]}'
        attempts[key] = attempts.get(key, 0) + 1
        if sub.get("verdict") == "OK" and key not in accepted:
            accepted[key] = {
                "site": "codeforces",
                "problem_key": key,
                "title": p["name"],
                "url": f'https://codeforces.com/problemset/problem/{p.get("contestId")}/{p["index"]}',
                "tags": ",".join(p.get("tags", [])),
                "difficulty": str(p["rating"]) if p.get("rating") else None,
                "modules": ",".join(modules_for_tags(p.get("tags", []), CF_TAG_MODULES)),
                "solved_at": datetime.fromtimestamp(sub["creationTimeSeconds"]).isoformat(sep=" "),
                "attempts": attempts[key],
            }
    new = sum(_upsert(conn, row) for row in accepted.values())
    u = info["result"][0]
    summary = f"rating {u.get('rating', 'unrated')}, max {u.get('maxRating', '-')}, rank {u.get('rank', '-')}"
    conn.execute(
        "INSERT INTO external_stats(site, fetched_at, summary) VALUES ('codeforces', ?, ?) "
        "ON CONFLICT(site) DO UPDATE SET fetched_at = excluded.fetched_at, summary = excluded.summary",
        (db.now(), summary),
    )
    return len(accepted), new, summary


# ---------------------------------------------------------------- LeetCode

LC_URL = "https://leetcode.com/graphql"
LC_HEADERS = {"Content-Type": "application/json", "Referer": "https://leetcode.com"}


def _lc(query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    data = _get_json(LC_URL, data=body, headers=LC_HEADERS)
    if "errors" in data and not data.get("data"):
        raise SyncError(f"LeetCode error: {data['errors'][0].get('message')}")
    return data["data"]


def leetcode_question(slug: str) -> dict | None:
    q = "query($s: String!) { question(titleSlug: $s) { questionFrontendId title difficulty topicTags { slug } } }"
    try:
        return _lc(q, {"s": slug}).get("question")
    except SyncError:
        return None


def sync_leetcode(conn: sqlite3.Connection, username: str) -> tuple[int, int, str]:
    if not username:
        raise SyncError("Set your username first: learn config set accounts.leetcode_username <name>")
    q = """
    query($u: String!, $l: Int!) {
      matchedUser(username: $u) { submitStatsGlobal { acSubmissionNum { difficulty count } } }
      recentAcSubmissionList(username: $u, limit: $l) { title titleSlug timestamp }
    }"""
    data = _lc(q, {"u": username, "l": 20})
    if data.get("matchedUser") is None:
        raise SyncError("LeetCode user not found, or the profile is private.")
    counts = {r["difficulty"]: r["count"] for r in data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]}
    summary = (
        f"solved {counts.get('All', 0)} "
        f"(easy {counts.get('Easy', 0)}, medium {counts.get('Medium', 0)}, hard {counts.get('Hard', 0)})"
    )
    recent = data.get("recentAcSubmissionList") or []
    new = 0
    for s in recent:
        info = leetcode_question(s["titleSlug"]) or {}
        tags = [t["slug"] for t in info.get("topicTags", [])]
        row = {
            "site": "leetcode",
            "problem_key": s["titleSlug"],
            "title": s["title"],
            "url": f'https://leetcode.com/problems/{s["titleSlug"]}/',
            "tags": ",".join(tags),
            "difficulty": info.get("difficulty"),
            "modules": ",".join(modules_for_tags(tags, LC_TAG_MODULES)),
            "solved_at": datetime.fromtimestamp(int(s["timestamp"])).isoformat(sep=" "),
            "attempts": None,
        }
        new += _upsert(conn, row)
    conn.execute(
        "INSERT INTO external_stats(site, fetched_at, summary) VALUES ('leetcode', ?, ?) "
        "ON CONFLICT(site) DO UPDATE SET fetched_at = excluded.fetched_at, summary = excluded.summary",
        (db.now(), summary),
    )
    logged = conn.execute("SELECT COUNT(*) FROM external_solves WHERE site = 'leetcode'").fetchone()[0]
    if counts.get("All", 0) > logged:
        summary += f". {counts['All'] - logged} solve(s) are not in your tracker; log them with learn log lc <slug>"
    return len(recent), new, summary
