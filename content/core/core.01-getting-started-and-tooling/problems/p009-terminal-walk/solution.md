## Walkthrough

| Command | Output | Why |
|---|---|---|
| `pwd` | `/home/asha` | we just moved there |
| `mkdir projects`, `cd projects` | nothing | |
| `pwd` | `/home/asha/projects` | |
| `cd ..`, `pwd` | `/home/asha` | `..` is the parent |
| `cd ~/projects/../projects`, `pwd` | `/home/asha/projects` | the `..` cancels one `projects` |
| `echo ... > hello.py` | nothing | output went into the file |
| `cat hello.py` | `print('hi')` | the double quotes were for bash; they are not stored |
| `python3 hello.py` | `hi` | |
| `echo hello \| wc -c` | `6` | 5 letters + 1 newline |
