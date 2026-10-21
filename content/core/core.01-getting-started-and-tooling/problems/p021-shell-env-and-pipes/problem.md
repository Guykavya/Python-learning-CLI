# Shell variables, export and pipes

Predict everything this bash session prints. Start in an empty folder. Commands
that print nothing contribute no lines.

```bash
$ mkdir -p demo/notes
$ cd demo
$ echo "apple" > fruits.txt
$ echo "banana" >> fruits.txt
$ echo "cherry" >> fruits.txt
$ cat fruits.txt | wc -l
$ ls | wc -l
$ grep an fruits.txt
$ COLOR=blue
$ echo $COLOR
$ python3 -c 'import os; print(os.environ.get("COLOR"))'
$ export COLOR
$ python3 -c 'import os; print(os.environ.get("COLOR"))'
$ LEVEL=pro python3 -c 'import os; print(os.environ.get("LEVEL"))'
$ python3 -c 'import os; print(os.environ.get("LEVEL"))'
$ echo "kiwi" > fruits.txt
$ cat fruits.txt | wc -l
```

Write the output in `answer.txt`, one line per output line.

**Format example**

For `echo hi` then `echo hi | wc -l`, the answer is:
```
hi
1
```
