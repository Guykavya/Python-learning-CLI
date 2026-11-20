# Problem plan: dsa.15 Tries and string algorithms (30 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.15.p001`…`p030`.
**Mix:** 8 drill, 12 applied, 8 deep, 2 challenge. Kinds: 24 code, 4 trace, 2 explain. **assessment:** explain = p008, trace = p012, fix = p018, build = p030.
String search tests compare with `str.find` / `re` on random strings over a tiny alphabet (`"ab"`), which produces many partial matches. Performance tests use 10**5–10**6 characters and make quadratic code time out with the message "worst case: repeated pattern like aaaa...b".

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Trie with dict nodes ✅ | drill | code | `insert/search/starts_with`; empty string; prefix is not a word |
| 2 | Trie with array nodes ✅ | drill | code | 26-letter array; same tests as p1 |
| 3 | Count words with a prefix ✅ | drill | code | counts stored in nodes |
| 4 | Delete a word from a trie ✅ | applied | code | prunes empty branches; node count checked |
| 5 | Autocomplete ✅ | applied | code | top 3 alphabetical; empty prefix |
| 6 | Longest common prefix ✅ | drill | code | |
| 7 | Replace words (root dictionary) ✅ | applied | code | shortest root |
| 8 | Why a trie and not a set of prefixes? ✅ | drill | explain | memory/time argument; graded by terms |
| 9 | Wildcard search `.` ✅ | applied | code | `add_word/search` with `.` |
| 10 | Word Search II ✅ | challenge | code | trie guiding DFS; 12x12 board time limit |
| 11 | Maximum XOR of two numbers ✅ | deep | code | binary trie; vs O(n²) |
| 12 | Trace a trie insertion ✅ | drill | trace | `⚠ HAND-TRACE` nodes created and counts after inserting 4 words |
| 13 | Prefix function by hand ✅ | drill | trace | `⚠ HAND-TRACE` pi array for `"abacabab"` |
| 14 | Prefix function ✅ | applied | code | vs brute force |
| 15 | KMP search ✅ | applied | code | all occurrences; overlapping; empty pattern rule |
| 16 | Trace KMP failure links ✅ | applied | trace | `⚠ HAND-TRACE` each comparison step when searching `"aabaab"` in `"aaabaaab"` |
| 17 | Smallest period of a string ✅ | applied | code | `n - pi[-1]` |
| 18 | Fix the naive search ✅ | applied | code | `assessment = "fix"`; given a quadratic search that times out on `"aaaa…b"`, switch to KMP |
| 19 | Repeated substring pattern ✅ | applied | code | |
| 20 | Shortest palindrome (prefix function) ✅ | deep | code | |
| 21 | Z-function ✅ | applied | code | vs brute force |
| 22 | Pattern search with Z ✅ | deep | code | |
| 23 | Count distinct substrings ✅ | deep | code | n ≤ 2,000; z or trie |
| 24 | Rabin-Karp search ✅ | applied | code | double modulus; collision test with a crafted pair |
| 25 | Longest repeated substring ✅ | deep | code | binary search + rolling hash; vs brute force |
| 26 | Manacher's algorithm ✅ | challenge | code | vs expand-around-centre |
| 27 | Longest palindromic substring in O(n) ✅ | deep | code | |
| 28 | Which tool for which string problem? ✅ | drill | explain | classify 8 tasks; graded by the label dictionary |
| 29 | Trace Manacher ✅ | deep | trace | `⚠ HAND-TRACE` centre, right edge and radius array for `"abaxaba"` |
| 30 | Build a string toolkit ✅ | deep | code | `assessment = "build"`; `Trie`, `kmp_search`, `z_function` in one module with a shared test; each compared with the built-ins |

## Counts
Written 2026-11-19 as the table says: 4 traces (p012, p013, p016, p029) and 2 explain (p008, p028). The older idea of extra trace/explain variants of p3, p4, p14, p21 and p24 was dropped. One assessment of each kind.

## Real-site problems (`external.toml`)
LeetCode `implement-trie-prefix-tree`, `design-add-and-search-words-data-structure`, `replace-words`, `longest-common-prefix`, `word-search-ii`, `maximum-xor-of-two-numbers-in-an-array`, `implement-strstr`, `find-the-index-of-the-first-occurrence-in-a-string`, `repeated-substring-pattern`, `shortest-palindrome`, `longest-duplicate-substring`, `longest-palindromic-substring`, `palindromic-substrings`, `search-suggestions-system`, `map-sum-pairs`; CSES 1753 (String Matching), 1732 (Finding Borders), 1733 (Finding Periods), 1111 (Palindrome Queries or Longest Palindrome) to verify. Ids unverified.
