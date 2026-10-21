## Walkthrough

| Command | Output | Why |
|---|---|---|
| `cat fruits.txt \| wc -l` | `3` | three lines were written (`>` then two `>>`) |
| `ls \| wc -l` | `2` | `fruits.txt` and the folder `notes` |
| `grep an fruits.txt` | `banana` | only `banana` contains `an` (apple and cherry do not) |
| `echo $COLOR` | `blue` | the shell itself knows the variable |
| first `python3 -c` | `None` | not exported, so the child process did not receive it |
| after `export` | `blue` | exported variables are copied into children |
| `LEVEL=pro python3 ...` | `pro` | set just for that one command |
| next `python3 ...` | `None` | the one-command setting did not stay |
| after `echo "kiwi" > fruits.txt` | `1` | `>` replaced the file with one line |
