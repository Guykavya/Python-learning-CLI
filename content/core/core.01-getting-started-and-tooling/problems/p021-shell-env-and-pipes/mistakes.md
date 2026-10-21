- Answering `blue` for the first `python3 -c`. The variable lives in the shell
  only; child processes get a copy of the *exported* variables.
- Answering `1` for `ls | wc -l`, forgetting the `notes` folder (folders are
  listed too).
- Expecting `pro` the second time. A `NAME=value command` prefix applies to that
  command only.
- Answering `4` at the end, as if `>` appended. `>` overwrites; `>>` appends.
