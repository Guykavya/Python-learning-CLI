## Walkthrough

| Step | Output | Why |
|---|---|---|
| (1) | `?? notes.txt` | new file, never added: untracked |
| (2) | `A  notes.txt` | staged as a new file (left column `A`) |
| (3) | `(clean)` | everything is committed; Git prints nothing |
| (4) | ` M notes.txt` | modified in the folder, not staged: **right** column |
| (5) | `M  notes.txt` | the change is now staged: **left** column |
| (6) | `M  notes.txt` and `?? todo.txt` | the staged change remains; the new file is untracked |

The leading space in (4) is the empty left column. It is the only way to tell
"modified, not staged" from "modified and staged" in short format.
